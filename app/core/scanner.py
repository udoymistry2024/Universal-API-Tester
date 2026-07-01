import asyncio
from typing import List, Callable, Dict, Any
import httpx
from app.providers.base import BaseProvider, ModelInfo
from app.core.tester import ModelTester
from app.utils.logger import log_scan_start, log_scan_end, log_error

class ModelScanner:
    def __init__(self, provider: BaseProvider, api_key: str, concurrency: int = 5, timeout: float = 15.0, retry_count: int = 2):
        self.provider = provider
        self.api_key = api_key
        self.concurrency = concurrency
        self.timeout = timeout
        self.retry_count = retry_count

    async def scan(self, progress_callback: Callable[[int, int, str], None] = None) -> List[Dict[str, Any]]:
        """
        List all models and test them concurrently.
        progress_callback receives (completed_count, total_count, current_model_id).
        """
        log_scan_start(self.provider.display_name)
        
        limits = httpx.Limits(max_keepalive_connections=self.concurrency, max_connections=self.concurrency * 2)
        async with httpx.AsyncClient(timeout=self.timeout, limits=limits) as client:
            try:
                # 1. Fetch available models
                models = await self.provider.list_models(self.api_key, client)
            except Exception as e:
                log_error(self.provider.provider_id, f"Failed to list models: {str(e)}")
                raise e

            total = len(models)
            results = []
            
            if total == 0:
                log_scan_end(self.provider.display_name, 0, 0, 0)
                return []

            tester = ModelTester(
                provider=self.provider,
                api_key=self.api_key,
                concurrency=self.concurrency,
                timeout=self.timeout,
                retry_count=self.retry_count
            )

            # Track progress count in a thread-safe / async-safe manner
            completed_lock = asyncio.Lock()
            completed_count = 0
            
            async def run_test(model: ModelInfo):
                nonlocal completed_count
                
                # Perform the test
                res = await tester.test_single_model(model.id, client)
                
                async with completed_lock:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total, model.id)
                
                return model, res

            # Update initial status
            if progress_callback:
                progress_callback(0, total, "Initializing scan...")

            # Run tests concurrently using Semaphore inside tester
            tasks = [run_test(model) for model in models]
            tested_pairs = await asyncio.gather(*tasks)
            
            working_count = 0
            failed_count = 0
            
            for model, res in tested_pairs:
                if res.status == "Working":
                    working_count += 1
                else:
                    failed_count += 1
                
                results.append({
                    "provider": self.provider.display_name,
                    "model_name": model.name,
                    "model_id": model.id,
                    "context_window": model.capabilities.context_window or "Unknown",
                    "input_token_limit": model.capabilities.input_token_limit or "Unknown",
                    "output_token_limit": model.capabilities.output_token_limit or "Unknown",
                    "supports_vision": model.capabilities.supports_vision,
                    "supports_images": model.capabilities.supports_images,
                    "supports_audio": model.capabilities.supports_audio,
                    "supports_video": model.capabilities.supports_video,
                    "supports_tools": model.capabilities.supports_tools,
                    "supports_json": model.capabilities.supports_json,
                    "supports_streaming": model.capabilities.supports_streaming,
                    "supports_reasoning": model.capabilities.supports_reasoning,
                    "supports_embeddings": model.capabilities.supports_embeddings,
                    "supports_finetuning": model.capabilities.supports_finetuning,
                    "supports_batch": model.capabilities.supports_batch,
                    "supports_multimodal": model.capabilities.supports_multimodal,
                    "status": res.status,
                    "latency": res.latency,
                    "error_message": res.error_message or ""
                })
                
            log_scan_end(self.provider.display_name, total, working_count, failed_count)
            
            # Sort results by status ("Working" first) then model name
            results.sort(key=lambda x: (x["status"] != "Working", x["model_id"]))
            return results
