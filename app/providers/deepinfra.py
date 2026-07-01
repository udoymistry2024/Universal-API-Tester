from app.providers.common import OpenAICompatibleProvider

class DeepInfraProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="deepinfra",
            display_name="DeepInfra",
            base_url="https://api.deepinfra.com/v1/openai",
            models_path="/models"
        )
