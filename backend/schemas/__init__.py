from __future__ import annotations

from backend.schemas.auth import (  # noqa: F401
    ChangePasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.schemas.chat import ChatHistoryResponse, ChatMessage, ChatRequest  # noqa: F401
from backend.schemas.generation import (  # noqa: F401
    GenerationListResponse,
    GenerationResponse,
    ImageGenerationRequest,
    VideoGenerationRequest,
)
from backend.schemas.providers import (  # noqa: F401
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)