from app.providers.common import OpenAICompatibleProvider

class GroqProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="groq",
            display_name="Groq",
            base_url="https://api.groq.com/openai/v1",
            models_path="/models"
        )
