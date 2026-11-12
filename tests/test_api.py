from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLE = (Path(__file__).resolve().parents[1] / "sample_data" / "sales.csv").read_text()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_sales_endpoint():
    response = client.post("/sales/summary", content=SAMPLE, headers={"content-type": "text/csv"})
    assert response.status_code == 200
    assert response.json()["total_revenue"] == 570.0


def test_invalid_csv():
    response = client.post("/sales/summary", content="invalid,column\n1,2")
    assert response.status_code == 422
