from __future__ import annotations

from app.schemas.auth import (  # noqa: F401
    ChangePasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.schemas.chat import ChatHistoryResponse, ChatMessage, ChatRequest  # noqa: F401
from app.schemas.generation import (  # noqa: F401
    GenerationListResponse,
    GenerationResponse,
    ImageGenerationRequest,
    VideoGenerationRequest,
)
from app.schemas.providers import (  # noqa: F401
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)