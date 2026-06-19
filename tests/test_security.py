import pytest

from app.core.security import create_access_token, decode_access_token, create_refresh_token


def test_create_access_token():
    token = create_access_token(subject='1')
    payload = decode_access_token(token)
    assert payload['sub'] == '1'
    assert payload['type'] == 'access'


def test_create_refresh_token():
    token = create_refresh_token(subject='1')
    payload = decode_access_token(token)

    assert payload['sub'] == '1'
    assert payload['type'] == 'refresh'
    assert 'jti' in payload