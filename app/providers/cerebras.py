from app.providers.common import OpenAICompatibleProvider

class CerebrasProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="cerebras",
            display_name="Cerebras",
            base_url="https://api.cerebras.ai/v1",
            models_path="/models"
        )
