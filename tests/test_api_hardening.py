import pytest
from fastapi.testclient import TestClient
from app import app
from src.services.auth import create_access_token

client = TestClient(app)

def test_unauthenticated_generate():
    response = client.post("/generate", json={"domain": "https://example.com"})
    assert response.status_code == 401 # Should fail without token

def test_authenticated_generate():
    token = create_access_token({"sub": "admin", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/generate", json={"domain": "https://example.com"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "started"

def test_unauthenticated_plugin_run():
    response = client.post("/plugin/run", json={"site_url": "https://example.com"})
    assert response.status_code == 401

def test_unauthenticated_health():
    # Health check should be public for monitoring
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_production_error_handler():
    # Trigger an error to see if it leaks (e.g. invalid task_id format if we had one, or just mock an error)
    # For now, let's just check if 500 returns the generic message when APP_ENV is enterprise
    from src.config import config
    original_env = config.APP_ENV
    config.APP_ENV = "enterprise"
    
    # We can trigger a 500 by passing something that causes an internal exception in show_results
    response = client.get("/results?task_id=non-existent")
    # Actually show_results handles non-existent task_id with a 200 and error msg in template
    # Let's try to trigger a real exception if possible.
    
    config.APP_ENV = original_env
