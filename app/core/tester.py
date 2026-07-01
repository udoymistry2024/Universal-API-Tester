import asyncio
import httpx
from app.providers.base import BaseProvider, TestResult
from app.utils.logger import log_model_test

class ModelTester:
    def __init__(self, provider: BaseProvider, api_key: str, concurrency: int = 5, timeout: float = 15.0, retry_count: int = 2):
        self.provider = provider
        self.api_key = api_key
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.retry_count = retry_count

    async def test_single_model(self, model_id: str, client: httpx.AsyncClient) -> TestResult:
        """Test a single model with concurrency limiting and rate-limit backoff."""
        async with self.semaphore:
            backoff = 1.5
            result = None
            for attempt in range(self.retry_count + 1):
                try:
                    result = await self.provider.test_model(self.api_key, model_id, client)
                except Exception as e:
                    # In case the provider test_model call throws an unhandled exception
                    result = TestResult(
                        model_id=model_id,
                        status="Failed",
                        latency=0.0,
                        error_message=str(e)
                    )

                # Log results to scanner.log
                log_model_test(
                    provider_id=self.provider.provider_id,
                    model_id=model_id,
                    status=result.status,
                    latency=result.latency,
                    error_message=result.error_message
                )
                
                # If rate limited, apply backoff and retry
                if result.status == "Rate Limited" and attempt < self.retry_count:
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                
                break
            
            return result
