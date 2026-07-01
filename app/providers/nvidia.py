from app.providers.common import OpenAICompatibleProvider

class NvidiaProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="nvidia",
            display_name="NVIDIA NIM",
            base_url="https://integrate.api.nvidia.com/v1",
            models_path="/models"
        )
