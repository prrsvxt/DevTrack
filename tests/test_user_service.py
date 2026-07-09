import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    create_refresh_token,
)
from app.services.user_service import UserService
from app.exceptions.token import TokenBlacklistedError


class FakeRedis:
    def __init__(self):
        self.storage = {}

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.storage[key] = value


class FakeUserRepository:
    def __init__(self, user=None):
        self.user = user

    async def get_by_id(self, user_id: int):
        return self.user


class FakeUser:
    def __init__(self, id: int):
        self.id = id


@pytest.mark.anyio
async def test_rotate_refresh_token_success():
    user_id = "1"
    old_refresh_token = create_refresh_token(user_id)
    old_payload = decode_access_token(old_refresh_token)
    old_jti = old_payload["jti"]

    fake_redis = FakeRedis()
    fake_user = FakeUser(id=1)

    service = UserService(session=None, redis_client=fake_redis)
    service.user_repository = FakeUserRepository(user=fake_user)

    access_token, new_refresh_token = await service.rotate_refresh_token(
        old_refresh_token
    )

    access_payload = decode_access_token(access_token)
    new_refresh_payload = decode_access_token(new_refresh_token)

    assert access_payload["sub"] == user_id
    assert access_payload["type"] == "access"

    assert new_refresh_payload["sub"] == user_id
    assert new_refresh_payload["type"] == "refresh"
    assert new_refresh_payload["jti"] != old_jti

    assert f"refresh:blacklist:{old_jti}" in fake_redis.storage


@pytest.mark.anyio
async def test_rotate_refresh_token_blacklisted():
    user_id = "1"

    old_refresh_token = create_refresh_token(user_id)
    old_payload = decode_access_token(old_refresh_token)
    old_jti = old_payload["jti"]

    fake_redis = FakeRedis()
    fake_redis.storage[f"refresh:blacklist:{old_jti}"] = "revoked"

    fake_user = FakeUser(id=1)

    service = UserService(session=None, redis_client=fake_redis)
    service.user_repository = FakeUserRepository(user=fake_user)

    with pytest.raises(TokenBlacklistedError):
        await service.rotate_refresh_token(old_refresh_token)


@pytest.mark.anyio
async def test_rotate_refresh_token_with_access_token():
    user_id = "1"

    access_token = create_access_token(subject=user_id)

    fake_redis = FakeRedis()
    fake_user = FakeUser(id=1)

    service = UserService(session=None, redis_client=fake_redis)
    service.user_repository = FakeUserRepository(user=fake_user)

    with pytest.raises(ValueError):
        await service.rotate_refresh_token(access_token)
