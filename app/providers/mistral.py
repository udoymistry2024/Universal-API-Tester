from app.providers.common import OpenAICompatibleProvider

class MistralProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="mistral",
            display_name="Mistral AI",
            base_url="https://api.mistral.ai/v1",
            models_path="/models"
        )
