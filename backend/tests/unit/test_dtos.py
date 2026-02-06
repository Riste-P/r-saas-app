from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.dto.auth import LoginRequest
from app.dto.user import CreateUserRequest, UpdateUserRequest


class TestLoginRequest:
    def test_valid(self):
        req = LoginRequest(email="user@example.com", password="secret")
        assert req.email == "user@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="secret")

    def test_missing_password_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com")


class TestCreateUserRequest:
    def test_defaults(self):
        req = CreateUserRequest(email="a@b.com", password="pw")
        assert req.role_id == 3
        assert req.tenant_id is None

    def test_with_tenant(self):
        tid = uuid4()
        req = CreateUserRequest(email="a@b.com", password="pw", tenant_id=tid)
        assert req.tenant_id == tid

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserRequest(email="bad", password="pw")


class TestUpdateUserRequest:
    def test_all_optional(self):
        req = UpdateUserRequest()
        assert req.role_id is None
        assert req.is_active is None

    def test_partial_update(self):
        req = UpdateUserRequest(is_active=False)
        assert req.is_active is False
        assert req.role_id is None
