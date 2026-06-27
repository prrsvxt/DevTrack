import pytest

from app.core.security import create_access_token, decode_access_token, create_refresh_token

@pytest.fixture
def user_id():
    return '1'

def test_create_access_token(user_id):
    token = create_access_token(subject=user_id)
    payload = decode_access_token(token)
    assert payload['sub'] == user_id
    assert payload['type'] == 'access'


def test_create_refresh_token(user_id):
    token = create_refresh_token(subject=user_id)
    payload = decode_access_token(token)

    assert payload['sub'] == user_id
    assert payload['type'] == 'refresh'
    assert 'jti' in payload

def decode_invalid_token():
    with pytest.raises(ValueError):
        decode_access_token('invalid_token')
