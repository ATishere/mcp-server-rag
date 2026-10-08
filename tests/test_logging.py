"""Test structured logging."""

import structlog

from mcp_rag.observability.logging import (
    add_app_info,
    add_context_vars,
    censor_sensitive_data,
    get_logger,
    log_context,
    new_request_id,
    request_id_var,
    setup_logging,
    user_id_var,
    workspace_id_var,
)


# ============================================================
# HELPERS
# ============================================================
class TestNewRequestId:
    def test_returns_string(self) -> None:
        rid = new_request_id()
        assert isinstance(rid, str)

    def test_length_16(self) -> None:
        rid = new_request_id()
        assert len(rid) == 16

    def test_unique(self) -> None:
        ids = {new_request_id() for _ in range(100)}
        assert len(ids) == 100


# ============================================================
# PROCESSORS
# ============================================================
class TestAddContextVars:
    def test_adds_request_id(self) -> None:
        token = request_id_var.set("req-123")
        try:
            event = add_context_vars(None, "info", {})
            assert event["request_id"] == "req-123"
        finally:
            request_id_var.reset(token)

    def test_adds_user_id(self) -> None:
        token = user_id_var.set("user-abc")
        try:
            event = add_context_vars(None, "info", {})
            assert event["user_id"] == "user-abc"
        finally:
            user_id_var.reset(token)

    def test_adds_workspace_id(self) -> None:
        token = workspace_id_var.set("ws-1")
        try:
            event = add_context_vars(None, "info", {})
            assert event["workspace_id"] == "ws-1"
        finally:
            workspace_id_var.reset(token)

    def test_empty_context(self) -> None:
        event = add_context_vars(None, "info", {"event": "test"})
        assert "request_id" not in event
        assert "user_id" not in event


class TestAddAppInfo:
    def test_adds_app_info(self) -> None:
        event = add_app_info(None, "info", {})
        assert "app" in event
        assert "version" in event
        assert "env" in event


class TestCensorSensitiveData:
    def test_censors_token(self) -> None:
        event = censor_sensitive_data(None, "info", {"token": "secret-123"})
        assert event["token"] == "***"

    def test_censors_password(self) -> None:
        event = censor_sensitive_data(None, "info", {"password": "abc"})
        assert event["password"] == "***"

    def test_censors_api_key(self) -> None:
        event = censor_sensitive_data(None, "info", {"api_key": "key-xyz"})
        assert event["api_key"] == "***"

    def test_censors_nested(self) -> None:
        event = censor_sensitive_data(
            None, "info", {"auth": {"token": "secret"}}
        )
        assert event["auth"]["token"] == "***"

    def test_censors_in_list(self) -> None:
        event = censor_sensitive_data(
            None, "info", {"items": [{"token": "secret"}, {"name": "safe"}]}
        )
        assert event["items"][0]["token"] == "***"
        assert event["items"][1]["name"] == "safe"

    def test_keeps_safe_data(self) -> None:
        event = censor_sensitive_data(None, "info", {"user": "alice"})
        assert event["user"] == "alice"


# ============================================================
# LOG CONTEXT
# ============================================================
class TestLogContext:
    def test_sets_and_resets_user_id(self) -> None:
        assert user_id_var.get() == ""
        with log_context(user_id="alice"):
            assert user_id_var.get() == "alice"
        assert user_id_var.get() == ""

    def test_sets_workspace_id(self) -> None:
        with log_context(workspace_id="ws-1"):
            assert workspace_id_var.get() == "ws-1"
        assert workspace_id_var.get() == ""

    def test_sets_request_id(self) -> None:
        with log_context(request_id="req-abc"):
            assert request_id_var.get() == "req-abc"
        assert request_id_var.get() == ""

    def test_sets_all(self) -> None:
        with log_context(
            request_id="req-1", user_id="alice", workspace_id="ws-1"
        ):
            assert request_id_var.get() == "req-1"
            assert user_id_var.get() == "alice"
            assert workspace_id_var.get() == "ws-1"

    def test_nested_contexts(self) -> None:
        with log_context(user_id="alice"):
            assert user_id_var.get() == "alice"
            with log_context(user_id="bob"):
                assert user_id_var.get() == "bob"
            assert user_id_var.get() == "alice"


# ============================================================
# SETUP
# ============================================================
class TestSetupLogging:
    def test_setup_runs(self) -> None:
        setup_logging()
        # Không raise là OK

    def test_get_logger(self) -> None:
        setup_logging()
        logger = get_logger("test")
        assert logger is not None

    def test_logger_can_log(self) -> None:
        setup_logging()
        logger = get_logger("test")
        # Không raise là OK
        logger.info("test_event", key="value")
