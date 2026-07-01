import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

DEFAULT_CONFIG = {
    "timeout": 15.0,
    "retry_count": 2,
    "concurrency": 5,
    "theme": "dark"
}

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception:
                # Fallback to default on invalid json
                pass
        
        # Override with environment variables if present
        config["timeout"] = float(os.getenv("TESTER_TIMEOUT", config["timeout"]))
        config["retry_count"] = int(os.getenv("TESTER_RETRY_COUNT", config["retry_count"]))
        config["concurrency"] = int(os.getenv("TESTER_CONCURRENCY", config["concurrency"]))
        config["theme"] = os.getenv("TESTER_THEME", config["theme"])
        
        return config

    @property
    def timeout(self) -> float:
        return float(self.config.get("timeout", 15.0))

    @property
    def retry_count(self) -> int:
        return int(self.config.get("retry_count", 2))

    @property
    def concurrency(self) -> int:
        return int(self.config.get("concurrency", 5))

    @property
    def theme(self) -> str:
        return str(self.config.get("theme", "dark"))

    def get_api_key(self, provider_id: str) -> str:
        """Attempt to fetch API key from environment variables."""
        env_var_name = f"{provider_id.upper()}_API_KEY"
        # Special case for Gemini
        if provider_id == "google":
            return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        return os.getenv(env_var_name, "")
