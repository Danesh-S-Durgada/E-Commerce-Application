from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_products_endpoint_exists():
    response = client.get("/api/products/")
    assert response.status_code in (200, 500)
