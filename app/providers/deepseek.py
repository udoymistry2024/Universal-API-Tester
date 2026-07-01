from app.providers.common import OpenAICompatibleProvider

class DeepSeekProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="deepseek",
            display_name="DeepSeek",
            base_url="https://api.deepseek.com",
            models_path="/models"
        )
