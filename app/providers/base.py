from abc import ABC, abstractmethod
from typing import Optional, List
import httpx
from pydantic import BaseModel, Field

class ModelCapability(BaseModel):
    context_window: Optional[int] = Field(None, description="Context window size in tokens")
    input_token_limit: Optional[int] = Field(None, description="Input token limit")
    output_token_limit: Optional[int] = Field(None, description="Output token limit")
    supports_vision: bool = Field(False, description="Supports image/vision input")
    supports_images: bool = Field(False, description="Supports generating images")
    supports_audio: bool = Field(False, description="Supports audio input/output")
    supports_video: bool = Field(False, description="Supports video input/output")
    supports_tools: bool = Field(False, description="Supports tool/function calling")
    supports_json: bool = Field(False, description="Supports JSON Mode output")
    supports_streaming: bool = Field(True, description="Supports chunked response streaming")
    supports_reasoning: bool = Field(False, description="Supports deep reasoning/thinking")
    supports_embeddings: bool = Field(False, description="Supports generating embeddings")
    supports_finetuning: bool = Field(False, description="Supports fine-tuning")
    supports_batch: bool = Field(False, description="Supports Batch API processing")
    supports_multimodal: bool = Field(False, description="Supports multimodal inputs")

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    capabilities: ModelCapability = Field(default_factory=ModelCapability)

class TestResult(BaseModel):
    model_id: str
    status: str  # Working, Not Accessible, Unsupported, Deprecated, Quota Exceeded, Rate Limited, Server Error, Invalid API Key
    latency: float  # response time in seconds
    error_message: Optional[str] = None

class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    @abstractmethod
    async def list_models(self, api_key: str, client: httpx.AsyncClient) -> List[ModelInfo]:
        """Fetch all models available for this provider using the API key."""
        pass

    @abstractmethod
    async def test_model(self, api_key: str, model_id: str, client: httpx.AsyncClient) -> TestResult:
        """Test a model via a small chat inference request."""
        pass
