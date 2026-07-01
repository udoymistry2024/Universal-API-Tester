from app.providers.common import OpenAICompatibleProvider

class TogetherProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="together",
            display_name="Together AI",
            base_url="https://api.together.xyz/v1",
            models_path="/models"
        )
