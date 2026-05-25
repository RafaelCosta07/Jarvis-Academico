from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
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
