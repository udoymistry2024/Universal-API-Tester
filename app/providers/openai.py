from app.providers.common import OpenAICompatibleProvider

class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="openai",
            display_name="OpenAI",
            base_url="https://api.openai.com/v1",
            models_path="/models"
        )
