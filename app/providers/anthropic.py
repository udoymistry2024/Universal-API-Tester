import time
from typing import List
import httpx
from app.providers.base import BaseProvider, ModelInfo, TestResult
from app.utils.exceptions import AuthenticationError, RateLimitError, ProviderError
from app.utils.model_db import guess_capabilities

class AnthropicProvider(BaseProvider):
    @property
    def provider_id(self) -> str:
        return "anthropic"

    @property
    def display_name(self) -> str:
        return "Anthropic"

    def _get_headers(self, api_key: str) -> dict:
        return {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        url = "https://api.anthropic.com/v1/models"
        try:
            response = await client.get(url, headers=self._get_headers(api_key))
            if response.status_code == 401:
                raise AuthenticationError("Invalid Anthropic API Key or Unauthorized access.", status_code=401, response_text=response.text)
            elif response.status_code == 403:
                raise AuthenticationError("Permission Denied (403) from Anthropic.", status_code=403, response_text=response.text)
            elif response.status_code == 429:
                raise RateLimitError("Rate limited when listing Anthropic models.", status_code=429, response_text=response.text)
            elif response.status_code >= 500:
                raise ProviderError(f"Anthropic server error: {response.status_code}", status_code=response.status_code, response_text=response.text)
            
            response.raise_for_status()
            data = response.json()
            
            models_data = data.get("data", [])
            results = []
            for item in models_data:
                model_id = item.get("id")
                display_name = item.get("display_name", model_id)
                if not model_id:
                    continue
                results.append(ModelInfo(
                    id=model_id,
                    name=display_name,
                    provider=self.provider_id,
                    capabilities=guess_capabilities(self.provider_id, model_id)
                ))
            
            results.sort(key=lambda x: x.id)
            return results
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP Connection error: {str(e)}")

    async def test_model(self, api_key: str, model_id: str, client: httpx.AsyncClient) -> TestResult:
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model_id,
            "max_tokens": 10,
            "messages": [
                {"role": "user", "content": "Reply with OK"}
            ]
        }
        
        start_time = time.perf_counter()
        try:
            response = await client.post(url, headers=self._get_headers(api_key), json=payload)
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
            elif status_code == 400:
                if "not supported" in error_msg.lower() or "unsupported" in error_msg.lower():
                    return TestResult(model_id=model_id, status="Unsupported", latency=latency, error_message=error_msg)
                return TestResult(model_id=model_id, status="Failed", latency=latency, error_message=error_msg)
            elif status_code == 429:
                if any(x in error_msg.lower() for x in ["quota", "billing", "credit", "balance", "limit reached"]):
                    return TestResult(model_id=model_id, status="Quota Exceeded", latency=latency, error_message=error_msg)
                return TestResult(model_id=model_id, status="Rate Limited", latency=latency, error_message=error_msg)
            elif status_code >= 500:
                return TestResult(model_id=model_id, status="Server Error", latency=latency, error_message=error_msg)
            else:
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
