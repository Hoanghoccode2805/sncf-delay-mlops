from fastapi.testclient import TestClient
from entrypoint.api import app

client = TestClient(app)
def test_health_check():
    """Check if the /health endpoint returns status 200 and the content 'ok'"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"