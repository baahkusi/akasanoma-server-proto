import falcon
from falcon import testing
import pytest
import json

from akasanoma.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_actions(client):
    payload = {
        "111": {
            "action_name": {},
            "000": ["action_name"]
        },

        "000": ["111", ]
    }

    expected = {
        "111": {
            "action_name": {"status":False,"data": "Invalid Action"},
        }
    }

    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json == expected
    assert response.status == falcon.HTTP_OK


def test_register(client):
    payload = {
        "111": {
            "register": {"email":"usebaku@gmail.com","device":"3229411841","user_type":"staff"},
            "000": ["register"]
        },

        "000": ["111", ]
    }

    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["register"]["status"]
    assert response.status == falcon.HTTP_OK


def test_login(client):
    payload = {
        "111": {
            "login": {
                "email":"usebaku@gmail.com",
                "device":"3229411841",
                "fresh_pin":4636326
                },
            "000": ["login"]
        },

        "000": ["111", ]
    }

    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["login"]["status"]
    assert response.status == falcon.HTTP_OK



def test_generate_pin(client):
    payload = {
        "111": {
            "generate_pin": {
                "email":"usebaku@gmail.com",
                "device":"3229411841",
                },
            "000": ["generate_pin"]
        },

        "000": ["111", ]
    }

    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["generate_pin"]["status"]
    assert response.status == falcon.HTTP_OK



















