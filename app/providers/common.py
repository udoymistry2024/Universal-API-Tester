import time
from typing import List, Optional
import httpx
from app.providers.base import BaseProvider, ModelInfo, TestResult
from app.utils.exceptions import AuthenticationError, RateLimitError, QuotaExceededError, ProviderError
from app.utils.model_db import guess_capabilities

class OpenAICompatibleProvider(BaseProvider):
    """Base provider class for all OpenAI-compatible API providers."""

    def __init__(self, provider_id: str, display_name: str, base_url: str, models_path: str = "/models", test_path: str = "/chat/completions"):
        self._provider_id = provider_id
        self._display_name = display_name
        self._base_url = base_url.rstrip("/")
        self._models_path = models_path
        self._test_path = test_path

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def display_name(self) -> str:
        return self._display_name

    def get_headers(self, api_key: str) -> dict:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        url = f"{self._base_url}{self._models_path}"
        try:
            response = await client.get(url, headers=self.get_headers(api_key))
            if response.status_code == 401:
                raise AuthenticationError("Invalid API Key or Unauthorized access.", status_code=401, response_text=response.text)
            elif response.status_code == 403:
                raise AuthenticationError("Permission Denied (403).", status_code=403, response_text=response.text)
            elif response.status_code == 429:
                raise RateLimitError("Rate limited when listing models.", status_code=429, response_text=response.text)
            elif response.status_code >= 500:
                raise ProviderError(f"Server error: {response.status_code}", status_code=response.status_code, response_text=response.text)
            
            response.raise_for_status()
            data = response.json()
            
            models_data = data.get("data", [])
            if not isinstance(models_data, list):
                models_data = []

            results = []
            for item in models_data:
                model_id = item.get("id")
                if not model_id:
                    continue
                results.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    provider=self.provider_id,
                    capabilities=guess_capabilities(self.provider_id, model_id)
                ))
            
            # Sort models alphabetically by ID
            results.sort(key=lambda x: x.id)
            return results
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP Connection error: {str(e)}")

    async def test_model(self, api_key: str, model_id: str, client: httpx.AsyncClient) -> TestResult:
        url = f"{self._base_url}{self._test_path}"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Reply with OK"}],
            "max_tokens": 10
        }
        
        start_time = time.perf_counter()
        try:
            response = await client.post(url, headers=self.get_headers(api_key), json=payload)
            latency = time.perf_counter() - start_time
            
            status_code = response.status_code
            if status_code == 200:
                return TestResult(model_id=model_id, status="Working", latency=latency)
            
            error_msg = ""
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text or f"HTTP {status_code}"

            if status_code == 401:
                return TestResult(model_id=model_id, status="Invalid API Key", latency=latency, error_message=error_msg)
            elif status_code == 403:
                return TestResult(model_id=model_id, status="Not Accessible", latency=latency, error_message=error_msg)
            elif status_code == 404:
                return TestResult(model_id=model_id, status="Unsupported", latency=latency, error_message=error_msg)
            elif status_code == 429:
                if any(x in error_msg.lower() for x in ["quota", "billing", "insufficient", "credit", "balance"]):
                    return TestResult(model_id=model_id, status="Quota Exceeded", latency=latency, error_message=error_msg)
                return TestResult(model_id=model_id, status="Rate Limited", latency=latency, error_message=error_msg)
            elif status_code >= 500:
                return TestResult(model_id=model_id, status="Server Error", latency=latency, error_message=error_msg)
            else:
                # Parse for general deprecated warnings
                if "deprecated" in error_msg.lower():
                    return TestResult(model_id=model_id, status="Deprecated", latency=latency, error_message=error_msg)
                return TestResult(model_id=model_id, status="Failed", latency=latency, error_message=error_msg)
                
        except httpx.TimeoutException:
            latency = time.perf_counter() - start_time
            return TestResult(model_id=model_id, status="Timeout", latency=latency, error_message="Request timed out")
        except httpx.HTTPError as e:
            latency = time.perf_counter() - start_time
            return TestResult(model_id=model_id, status="Network Error", latency=latency, error_message=str(e))
        except Exception as e:
            latency = time.perf_counter() - start_time
            return TestResult(model_id=model_id, status="Error", latency=latency, error_message=str(e))
