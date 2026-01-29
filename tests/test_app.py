import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)


def test_root_redirect_or_docs():
    """Проверяем, что приложение отвечает"""
    response = client.get("/docs")
    assert response.status_code in (200, 404) 

    response_root = client.get("/")
    assert response_root.status_code in (200, 404, 307, 308) 


def test_openapi_schema():
    """Проверяем OpenAPI-схему"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()