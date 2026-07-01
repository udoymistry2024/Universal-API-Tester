from app.providers.common import OpenAICompatibleProvider

class XAIProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="xai",
            display_name="xAI (Grok)",
            base_url="https://api.x.ai/v1",
            models_path="/models"
        )
