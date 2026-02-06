from uuid import uuid4

import jwt
import pytest

from app.core.config import settings
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("mypassword")
        assert not verify_password("wrongpassword", hashed)

    def test_hash_is_unique(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt salt makes each hash unique


class TestJWT:
    def test_access_token_roundtrip(self):
        user_id = uuid4()
        tenant_id = uuid4()
        token = create_access_token(user_id, tenant_id, "admin")
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["tid"] == str(tenant_id)
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        user_id = uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "tid" not in payload

    def test_invalid_token_raises(self):
        with pytest.raises(jwt.DecodeError):
            decode_token("not.a.token")

    def test_tampered_token_raises(self):
        token = create_access_token(uuid4(), uuid4(), "user")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(jwt.InvalidSignatureError):
            decode_token(tampered)

    def test_wrong_secret_raises(self):
        token = create_access_token(uuid4(), uuid4(), "user")
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "a-]different-secret-that-is-long-enough", algorithms=[settings.JWT_ALGORITHM])
