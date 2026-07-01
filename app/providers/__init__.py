from app.providers.openai import OpenAIProvider
from app.providers.anthropic import AnthropicProvider
from app.providers.google import GoogleProvider
from app.providers.deepseek import DeepSeekProvider
from app.providers.mistral import MistralProvider
from app.providers.nvidia import NvidiaProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.together import TogetherProvider
from app.providers.groq import GroqProvider
from app.providers.xai import XAIProvider
from app.providers.cerebras import CerebrasProvider
from app.providers.fireworks import FireworksProvider
from app.providers.opencode_zen import OpenCodeZenProvider
from app.providers.xiaomi import XiaomiProvider
from app.providers.cohere import CohereProvider
from app.providers.perplexity import PerplexityProvider
from app.providers.deepinfra import DeepInfraProvider

PROVIDERS = [
    OpenAIProvider(),
    AnthropicProvider(),
    GoogleProvider(),
    NvidiaProvider(),
    OpenRouterProvider(),
    DeepSeekProvider(),
    MistralProvider(),
    XAIProvider(),
    TogetherProvider(),
    GroqProvider(),
    CerebrasProvider(),
    FireworksProvider(),
    OpenCodeZenProvider(),
    XiaomiProvider(),
    CohereProvider(),
    PerplexityProvider(),
    DeepInfraProvider(),
]

