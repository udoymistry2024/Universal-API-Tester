import re
from typing import Dict, Any
from app.providers.base import ModelCapability

# Dictionary of well-known models and their actual capabilities
KNOWN_MODELS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "openai": {
        "gpt-4o": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 16384,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_batch": True, "supports_multimodal": True
        },
        "gpt-4o-mini": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 16384,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_batch": True, "supports_multimodal": True
        },
        "o1-preview": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 32768,
            "supports_vision": False, "supports_tools": False, "supports_json": False,
            "supports_streaming": True, "supports_reasoning": True
        },
        "o1-mini": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 65536,
            "supports_vision": False, "supports_tools": False, "supports_json": False,
            "supports_streaming": True, "supports_reasoning": True
        },
        "o3-mini": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 100000,
            "supports_vision": False, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_reasoning": True
        },
        "gpt-4-turbo": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 4096,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True
        },
        "gpt-4": {
            "context_window": 8192, "input_token_limit": 8192, "output_token_limit": 4096,
            "supports_vision": False, "supports_tools": True, "supports_json": False,
            "supports_streaming": True
        },
        "gpt-3.5-turbo": {
            "context_window": 16385, "input_token_limit": 16385, "output_token_limit": 4096,
            "supports_vision": False, "supports_tools": True, "supports_json": True,
            "supports_streaming": True
        }
    },
    "anthropic": {
        "claude-3-5-sonnet-latest": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True
        },
        "claude-3-5-haiku-latest": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 8192,
            "supports_vision": False, "supports_tools": True, "supports_json": True,
            "supports_streaming": True
        },
        "claude-3-opus-latest": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 4096,
            "supports_vision": True, "supports_tools": True, "supports_json": False,
            "supports_streaming": True, "supports_multimodal": True
        },
        "claude-3-sonnet-20240229": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 4096,
            "supports_vision": True, "supports_tools": True, "supports_streaming": True, "supports_multimodal": True
        },
        "claude-3-haiku-20240307": {
            "context_window": 200000, "input_token_limit": 200000, "output_token_limit": 4096,
            "supports_vision": True, "supports_tools": True, "supports_streaming": True, "supports_multimodal": True
        }
    },
    "google": {
        "gemini-1.5-flash": {
            "context_window": 1048576, "input_token_limit": 1048576, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True, "supports_audio": True, "supports_video": True
        },
        "gemini-1.5-pro": {
            "context_window": 2097152, "input_token_limit": 2097152, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True, "supports_audio": True, "supports_video": True
        },
        "gemini-2.0-flash": {
            "context_window": 1048576, "input_token_limit": 1048576, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True, "supports_audio": True, "supports_video": True
        },
        "gemini-2.5-flash": {
            "context_window": 1048576, "input_token_limit": 1048576, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True, "supports_audio": True, "supports_video": True
        },
        "gemini-2.5-pro": {
            "context_window": 2097152, "input_token_limit": 2097152, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_multimodal": True, "supports_audio": True, "supports_video": True
        }
    },
    "deepseek": {
        "deepseek-chat": {
            "context_window": 64000, "input_token_limit": 64000, "output_token_limit": 8192,
            "supports_vision": False, "supports_tools": True, "supports_json": True,
            "supports_streaming": True
        },
        "deepseek-reasoner": {
            "context_window": 64000, "input_token_limit": 64000, "output_token_limit": 8192,
            "supports_vision": False, "supports_tools": False, "supports_json": False,
            "supports_streaming": True, "supports_reasoning": True
        }
    },
    "xiaomi": {
        "mimo-v2.5-pro": {
            "context_window": 128000, "input_token_limit": 128000, "output_token_limit": 8192,
            "supports_vision": True, "supports_tools": True, "supports_json": True,
            "supports_streaming": True, "supports_reasoning": True, "supports_multimodal": True
        },
        "mimo-v2.5": {
            "context_window": 64000, "input_token_limit": 64000, "output_token_limit": 4096,
            "supports_vision": True, "supports_tools": True, "supports_streaming": True, "supports_multimodal": True
        },
        "mimo-v2.5-asr": {
            "context_window": 16384, "input_token_limit": 16384, "output_token_limit": 2048,
            "supports_audio": True, "supports_streaming": True
        }
    }
}

def guess_capabilities(provider_id: str, model_id: str) -> ModelCapability:
    """Guess capabilities for a model using its ID and provider heuristics."""
    # Look up in database first
    model_id_lower = model_id.lower()
    
    # Try exact match in known models
    if provider_id in KNOWN_MODELS:
        for known_id, caps in KNOWN_MODELS[provider_id].items():
            if known_id in model_id_lower:
                return ModelCapability(**caps)

    # Guess based on patterns
    caps_dict = {
        "context_window": 8192,
        "input_token_limit": 8192,
        "output_token_limit": 4096,
        "supports_vision": False,
        "supports_images": False,
        "supports_audio": False,
        "supports_video": False,
        "supports_tools": False,
        "supports_json": False,
        "supports_streaming": True,
        "supports_reasoning": False,
        "supports_embeddings": False,
        "supports_finetuning": False,
        "supports_batch": False,
        "supports_multimodal": False
    }

    # Vision / Multimodal detection
    if any(x in model_id_lower for x in ["vision", "vl", "pixtral", "llava", "multimodal", "gui"]):
        caps_dict["supports_vision"] = True
        caps_dict["supports_multimodal"] = True

    # Audio detection
    if any(x in model_id_lower for x in ["audio", "speech", "asr", "whisper", "tts"]):
        caps_dict["supports_audio"] = True

    # Video detection
    if "video" in model_id_lower:
        caps_dict["supports_video"] = True

    # Reasoning models (like o1, o3, deepseek-reasoner, R1, grok-2-reasoner, qwen-2.5-math/coder-instruct, thinking, reasoning)
    if any(x in model_id_lower for x in ["reasoner", "reasoning", "thinking", "r1", "math", "o1", "o3"]):
        caps_dict["supports_reasoning"] = True

    # Tool calling support (almost all modern models except specific ones)
    if any(x in model_id_lower for x in ["instruct", "chat", "preview", "latest", "pro", "flash", "mini", "sonnet", "haiku", "gpt-4", "gpt-3.5", "llama3", "llama-3", "mistral", "mixtral", "qwen", "gemma"]):
        caps_dict["supports_tools"] = True
        caps_dict["supports_json"] = True

    # Context window guessing based on model series
    if "claude" in model_id_lower:
        caps_dict["context_window"] = 200000
        caps_dict["input_token_limit"] = 200000
        caps_dict["output_token_limit"] = 8192
    elif "gemini" in model_id_lower:
        caps_dict["context_window"] = 1048576
        caps_dict["input_token_limit"] = 1048576
        caps_dict["output_token_limit"] = 8192
    elif "gpt-4" in model_id_lower or "o1" in model_id_lower or "o3" in model_id_lower:
        caps_dict["context_window"] = 128000
        caps_dict["input_token_limit"] = 128000
        caps_dict["output_token_limit"] = 16384
    elif "llama-3.3" in model_id_lower or "llama-3.1" in model_id_lower or "llama3.1" in model_id_lower or "llama3.3" in model_id_lower:
        caps_dict["context_window"] = 128000
        caps_dict["input_token_limit"] = 128000
        caps_dict["output_token_limit"] = 8192
    elif "llama3" in model_id_lower or "llama-3" in model_id_lower:
        caps_dict["context_window"] = 8192
        caps_dict["input_token_limit"] = 8192
        caps_dict["output_token_limit"] = 4096
    elif "qwen" in model_id_lower:
        caps_dict["context_window"] = 32768
        caps_dict["input_token_limit"] = 32768
        caps_dict["output_token_limit"] = 8192
    elif "mistral" in model_id_lower or "mixtral" in model_id_lower:
        caps_dict["context_window"] = 32768
        caps_dict["input_token_limit"] = 32768
        caps_dict["output_token_limit"] = 8192
    elif "command" in model_id_lower:
        caps_dict["context_window"] = 128000
        caps_dict["input_token_limit"] = 128000
        caps_dict["output_token_limit"] = 4096
    elif "sonar" in model_id_lower:
        caps_dict["context_window"] = 128000
        caps_dict["input_token_limit"] = 128000
        caps_dict["output_token_limit"] = 4096


    # Embeddings models
    if "embed" in model_id_lower:
        caps_dict["supports_embeddings"] = True
        caps_dict["supports_streaming"] = False

    return ModelCapability(**caps_dict)
