"""Shared fixtures cho tất cả tests."""

from typing import Any
import pytest

from mcp_rag.auth.jwt_handler import jwt_handler


# ============================================================
# AUTH FIXTURES
# ============================================================
@pytest.fixture
def admin_token() -> str:
    """JWT token với role admin."""
    return jwt_handler.create_token("test-admin", "admin")


@pytest.fixture
def editor_token() -> str:
    """JWT token với role editor."""
    return jwt_handler.create_token("test-editor", "editor")


@pytest.fixture
def viewer_token() -> str:
    """JWT token với role viewer."""
    return jwt_handler.create_token("test-viewer", "viewer")


@pytest.fixture
def invalid_token() -> str:
    """Token sai (đủ dài nhưng không hợp lệ)."""
    return "invalid-token-not-a-real-jwt-12345"


# ============================================================
# MOCK SERVICES
# ============================================================
@pytest.fixture
def mock_vector_store() -> Any:
    """Mock VectorStore trả fake data."""

    class MockVectorStore:
        async def hybrid_search(
            self,
            query: str,
            top_k: int = 10,
            filters: dict[str, Any] | None = None,
        ) -> list[dict[str, Any]]:
            return [
                {
                    "chunk_id": f"chunk-{i}",
                    "document_id": f"doc-{i}",
                    "content": f"Mock content {i} for query: {query}",
                    "score": 1.0 - i * 0.1,
                }
                for i in range(1, min(top_k, 4))
            ]

        async def get_chunk(self, chunk_id: str) -> dict[str, Any] | None:
            return {
                "chunk_id": chunk_id,
                "document_id": "doc-1",
                "chunk_index": 0,
                "content": f"Mock full content for chunk: {chunk_id}",
                "metadata": {"source": "mock.md"},
            }

    return MockVectorStore()


@pytest.fixture
def mock_reranker() -> Any:
    """Mock Reranker giữ nguyên thứ tự."""

    class MockReranker:
        async def rerank(
            self,
            query: str,
            documents: list[dict[str, Any]],
            top_k: int = 5,
        ) -> list[dict[str, Any]]:
            return documents[:top_k]

    return MockReranker()


@pytest.fixture
def mock_generator() -> Any:
    """Mock LLM Generator."""

    class MockGenerator:
        async def generate(self, query: str, context: list[str]) -> str:
            return (
                f"Mock answer for {query!r} based on "
                f"{len(context)} context chunks."
            )

    return MockGenerator()


@pytest.fixture
def mock_empty_vector_store() -> Any:
    """Mock VectorStore trả về rỗng."""

    class MockEmptyVectorStore:
        async def hybrid_search(self, query, top_k=10, filters=None):
            return []

        async def get_chunk(self, chunk_id):
            return None

    return MockEmptyVectorStore()
