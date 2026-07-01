from typing import List, Optional
from app.providers.base import BaseProvider
from app.providers import PROVIDERS

class ProviderManager:
    def __init__(self):
        self._providers = {p.provider_id: p for p in PROVIDERS}

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        return self._providers.get(provider_id)

    def list_providers(self) -> List[BaseProvider]:
        # Return providers in the exact order they are defined in __init__.py
        return list(self._providers.values())
