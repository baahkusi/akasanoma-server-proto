import pytest
from akasanoma.utils import fresh_pin, token


def test_pin():
    p = fresh_pin()
    assert p


def test_token():
    pin = fresh_pin()
    email = 'sbk@sbk.sbk'
    t = token(email, pin)
    assert t