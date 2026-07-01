from typing import List
import httpx
from app.providers.base import ModelInfo, TestResult
from app.providers.common import OpenAICompatibleProvider
from app.utils.model_db import guess_capabilities
from app.utils.exceptions import AuthenticationError, ProviderError

class PerplexityProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="perplexity",
            display_name="Perplexity",
            base_url="https://api.perplexity.ai",
            models_path="/models",
            test_path="/chat/completions"
        )

    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        # Perplexity does not support standard GET /models endpoint.
        # We pre-validate the API key by testing a request to its default 'sonar' model.
        url = f"{self._base_url}/chat/completions"
        headers = self.get_headers(api_key)
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 401:
                raise AuthenticationError("Invalid API Key or Unauthorized access.", status_code=401, response_text=response.text)
            elif response.status_code == 403:
                raise AuthenticationError("Permission Denied (403).", status_code=403, response_text=response.text)
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP Connection error during validation: {str(e)}")

        # Well-known Perplexity models
        model_ids = [
            "sonar",
            "sonar-pro",
            "sonar-reasoning",
            "llama-3-1-sonar-small-128k-chat",
            "llama-3-1-sonar-large-128k-chat",
            "llama-3-1-sonar-large-128k-online"
        ]
        return [
            ModelInfo(
                id=m,
                name=m,
                provider=self.provider_id,
                capabilities=guess_capabilities(self.provider_id, m)
            )
            for m in model_ids
        ]
