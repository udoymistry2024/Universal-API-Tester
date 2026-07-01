import time
from typing import List
import httpx
from app.providers.base import BaseProvider, ModelInfo, TestResult, ModelCapability
from app.utils.exceptions import AuthenticationError, RateLimitError, ProviderError
from app.utils.model_db import guess_capabilities

class GoogleProvider(BaseProvider):
    @property
    def provider_id(self) -> str:
        return "google"

    @property
    def display_name(self) -> str:
        return "Google AI Studio"

    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        try:
            response = await client.get(url)
            
            # Google often returns 400 or 403 for invalid API keys
            if response.status_code in [400, 403, 401]:
                err_text = response.text
                if "API key not valid" in err_text or "key is invalid" in err_text or "keyExpired" in err_text:
                    raise AuthenticationError("Invalid Google API Key.", status_code=response.status_code, response_text=err_text)
                elif "PermissionDenied" in err_text or "permission" in err_text.lower():
                    raise AuthenticationError("Permission Denied (403) from Google.", status_code=403, response_text=err_text)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limited when listing Google models.", status_code=429, response_text=response.text)
            elif response.status_code >= 500:
                raise ProviderError(f"Google server error: {response.status_code}", status_code=response.status_code, response_text=response.text)

            response.raise_for_status()
            data = response.json()
            
            models_data = data.get("models", [])
            results = []
            for item in models_data:
                full_name = item.get("name", "")  # e.g., "models/gemini-1.5-flash"
                if not full_name:
                    continue
                
                # Check if it supports generateContent
                methods = item.get("supportedGenerationMethods", [])
                if "generateContent" not in methods:
                    continue

                # Strip "models/" prefix for user display / guess capabilities
                short_name = full_name.split("/")[-1] if "/" in full_name else full_name
                
                # Grab limits if provided by API
                input_limit = item.get("inputTokenLimit")
                output_limit = item.get("outputTokenLimit")
                
                caps = guess_capabilities(self.provider_id, short_name)
                if input_limit:
                    caps.input_token_limit = input_limit
                    caps.context_window = input_limit
                if output_limit:
                    caps.output_token_limit = output_limit

                results.append(ModelInfo(
                    id=full_name,  # Keep the full path as ID for direct endpoint requests
                    name=item.get("displayName", short_name),
                    provider=self.provider_id,
                    capabilities=caps
                ))
            
            results.sort(key=lambda x: x.id)
            return results
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP Connection error: {str(e)}")

    async def test_model(self, api_key: str, model_id: str, client: httpx.AsyncClient) -> TestResult:
        # model_id is expected to be e.g. "models/gemini-1.5-flash"
        # URL template: https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent?key={api_key}
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Reply with OK"
                }]
            }]
        }
        
        start_time = time.perf_counter()
        try:
            response = await client.post(url, json=payload)
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

            if status_code in [400, 401]:
                if "API key not valid" in error_msg or "keyExpired" in error_msg:
                    return TestResult(model_id=model_id, status="Invalid API Key", latency=latency, error_message=error_msg)
                return TestResult(model_id=model_id, status="Unsupported", latency=latency, error_message=error_msg)
            elif status_code == 403:
                return TestResult(model_id=model_id, status="Not Accessible", latency=latency, error_message=error_msg)
            elif status_code == 404:
                return TestResult(model_id=model_id, status="Unsupported", latency=latency, error_message=error_msg)
            elif status_code == 429:
                if any(x in error_msg.lower() for x in ["quota", "exhausted", "billing", "budget"]):
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
