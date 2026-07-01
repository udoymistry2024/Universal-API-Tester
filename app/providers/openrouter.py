from app.providers.common import OpenAICompatibleProvider

class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="openrouter",
            display_name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            models_path="/models"
        )
