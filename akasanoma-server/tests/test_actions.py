import falcon
from falcon import testing
import pytest
import json

from akasanoma.app import api
from datauri import DataURI


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_get_progress(client):
    """
    :kwargs: 
    """
    payload = {
        "111": {
            "get_progress": {},
            "000": ["get_progress"]
        },

        "000": ["111", ]
    }
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["get_progress"]["status"]


def test_get_entries(client):
    """
    :kwargs: level
    """
    payload = {
        "111": {
            "get_entries": {"level": 2},
            "000": ["get_entries"]
        },

        "000": ["111", ]
    }
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["get_entries"]["status"]


def test_get_translations(client):
    """
    :kwargs: level
    """
    payload = {
        "111": {
            "get_translations": {"level": 1},
            "000": ["get_translations"]
        },

        "000": ["111", ]
    }
    
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["get_translations"]["status"]
    


def test_set_entries(client):
    """
    :kwargs: excel file
    """
    file = DataURI.from_file('tests/files/md.csv')
    payload = {
        "111": {
            "set_entries": {"file": file},
            "000": ["set_entries"]
        },

        "000": ["111", ]
    }

    response = client.simulate_post('/action', body=json.dumps(payload))

    assert response.json["111"]["set_entries"]["status"]


def test_set_translations(client):
    """
    :kwargs: trans
    """
    payload = {
        "111": {
            "set_translations": {"trans": [
                {"entry": "Entry", "id": 20, "trans": "A"},
                {"entry": "Entry", "id": 21, "trans": "B"},
                {"entry": "Entry", "id": 26, "trans": "C"}
            ]},
            "000": ["set_translations"]
        },

        "000": ["111", ]
    }

    response = client.simulate_post('/action', body=json.dumps(payload))

    assert response.json["111"]["set_translations"]["status"]


def test_set_validations(client):
    """
    :kwargs: valids
    """
    payload = {
        "111": {
            "set_validations": {"valids": [
                {"entry": "Entry", "trans": "Translation", 'id': 26, "rating": 100},
                {"entry": "Entry", "trans": "Translation", 'id': 27, "rating": 90},
                {"entry": "Entry", "trans": "Translation", 'id': 28, "rating": 90}
            ], "level":1},
            "000": ["set_validations"]
        },

        "000": ["111", ]
    }
    
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["set_validations"]["status"]


def test_all_entries(client):
    """
    :kwargs: block, block_size
    """
    payload = {
        "111": {
            "all_entries": {"block": 2,"block_size": 10},
            "000": ["all_entries"]
        },

        "000": ["111", ]
    }
    
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["all_entries"]["status"]


def test_all_translations(client):
    """
    :kwargs: block, block_size
    """
    payload = {
        "111": {
            "all_translations": {"block": 1,"block_size": 10},
            "000": ["all_translations"]
        },

        "000": ["111", ]
    }
    
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["all_translations"]["status"]


def test_all_validations(client):
    """
    :kwargs: block, block_size
    """
    payload = {
        "111": {
            "all_validations": {"block": 1,"block_size": 10},
            "000": ["all_validations"]
        },

        "000": ["111", ]
    }
    
    response = client.simulate_post('/action', body=json.dumps(payload))
    
    assert response.json["111"]["all_validations"]["status"]
