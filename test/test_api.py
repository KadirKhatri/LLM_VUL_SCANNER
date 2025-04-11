import pytest
from app.api import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}

def test_scan_missing_model_path(client):
    response = client.post('/scan', json={})
    assert response.status_code == 400
    assert 'model_path is required' in response.json['error']

def test_scan_invalid_model(client):
    response = client.post('/scan', json={'model_path': 'invalid/model'})
    assert response.status_code == 500
    assert 'Failed to load model' in response.json['error']