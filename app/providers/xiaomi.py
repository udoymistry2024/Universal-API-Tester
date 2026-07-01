from typing import List
import httpx
from app.providers.common import OpenAICompatibleProvider
from app.providers.base import ModelInfo, TestResult

class XiaomiProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="xiaomi",
            display_name="Xiaomi AI Studio",
            base_url="https://api.xiaomimimo.com/v1",
            models_path="/models"
        )

    def _select_base_url(self, api_key: str):
        if api_key.strip().startswith("tp-"):
            self._base_url = "https://token-plan-cn.xiaomimimo.com/v1"
        else:
            self._base_url = "https://api.xiaomimimo.com/v1"

    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        self._select_base_url(api_key)
        return await super().list_models(api_key, client)

    async def test_model(self, api_key: str, model_id: str, client: httpx.AsyncClient) -> TestResult:
        self._select_base_url(api_key)
        return await super().test_model(api_key, model_id, client)
