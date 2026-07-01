from app.providers.common import OpenAICompatibleProvider

class FireworksProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="fireworks",
            display_name="Fireworks AI",
            base_url="https://api.fireworks.ai/inference/v1",
            models_path="/models"
        )
