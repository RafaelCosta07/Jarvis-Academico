from typing import Any, Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag_service import RAGService


@runtime_checkable
class ToolExecutor(Protocol):
    async def __call__(
        self,
        input_data: dict[str, Any],
        db: AsyncSession,
        rag_service: RAGService,
        **kwargs: Any,
    ) -> dict[str, Any]: ...
