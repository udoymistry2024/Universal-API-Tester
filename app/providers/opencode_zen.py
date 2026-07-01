from app.providers.common import OpenAICompatibleProvider

class OpenCodeZenProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            provider_id="opencode_zen",
            display_name="OpenCode Zen",
            base_url="https://opencode.ai/zen/v1",
            models_path="/models"
        )
