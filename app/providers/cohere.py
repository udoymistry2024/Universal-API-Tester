from app.providers.common import OpenAICompatibleProvider

class CohereProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="cohere",
            display_name="Cohere",
            base_url="https://api.cohere.com/compatibility/v1",
            models_path="/models"
        )
