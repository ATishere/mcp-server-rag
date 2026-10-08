"""Test JWT + RBAC."""

import pytest

from mcp_rag.auth.jwt_handler import jwt_handler
from mcp_rag.auth.rbac import (
    Permission,
    Role,
    get_permissions,
    has_permission,
    require_permission,
)


# ============================================================
# JWT TESTS
# ============================================================
class TestJWTHandler:
    def test_create_token(self) -> None:
        token = jwt_handler.create_token("alice", "admin")
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_valid_token(self) -> None:
        token = jwt_handler.create_token("alice", "admin")
        payload = jwt_handler.verify_token(token)
        assert payload["sub"] == "alice"
        assert payload["role"] == "admin"

    def test_verify_invalid_token(self) -> None:
        with pytest.raises(PermissionError):
            jwt_handler.verify_token("invalid-token")

    def test_verify_expired_token(self) -> None:
        token = jwt_handler.create_token("alice", "admin", expires_minutes=-1)
        with pytest.raises(PermissionError):
            jwt_handler.verify_token(token)

    def test_token_with_scopes(self) -> None:
        token = jwt_handler.create_token(
            "alice", "admin", scopes=["read", "write"]
        )
        payload = jwt_handler.verify_token(token)
        assert "read" in payload["scopes"]
        assert "write" in payload["scopes"]

    def test_token_with_extra_claims(self) -> None:
        token = jwt_handler.create_token(
            "alice", "admin", extra_claims={"workspace_id": "ws-1"}
        )
        payload = jwt_handler.verify_token(token)
        assert payload["workspace_id"] == "ws-1"


# ============================================================
# RBAC TESTS
# ============================================================
class TestRBAC:
    @pytest.mark.parametrize(
        "role,permission,expected",
        [
            ("admin", Permission.READ, True),
            ("admin", Permission.WRITE, True),
            ("admin", Permission.DELETE, True),
            ("admin", Permission.ADMIN, True),
            ("editor", Permission.READ, True),
            ("editor", Permission.WRITE, True),
            ("editor", Permission.DELETE, False),
            ("viewer", Permission.READ, True),
            ("viewer", Permission.WRITE, False),
            ("viewer", Permission.DELETE, False),
            ("unknown", Permission.READ, False),
        ],
    )
    def test_has_permission(
        self, role: str, permission: Permission, expected: bool
    ) -> None:
        assert has_permission(role, permission) == expected

    def test_get_permissions_admin(self) -> None:
        perms = get_permissions("admin")
        assert Permission.READ in perms
        assert Permission.WRITE in perms
        assert Permission.DELETE in perms

    def test_get_permissions_viewer(self) -> None:
        perms = get_permissions("viewer")
        assert perms == {Permission.READ}

    def test_require_permission_ok(self) -> None:
        require_permission("admin", Permission.DELETE)

    def test_require_permission_fail(self) -> None:
        with pytest.raises(PermissionError):
            require_permission("viewer", Permission.DELETE)

    def test_unknown_role_returns_empty(self) -> None:
        assert get_permissions("unknown") == set()
