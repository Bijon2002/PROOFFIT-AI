import io
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_list_use_cases():
    res = client.get("/api/use-cases")
    assert res.status_code == 200
    data = res.json()
    assert "demand_forecasting" in data
    assert "required" in data["demand_forecasting"]

def test_sample_datasets():
    res = client.get("/api/sample-datasets")
    assert res.status_code == 200
    data = res.json()
    assert "samples" in data

def test_suggest_mapping_and_assess_flow():
    csv_content = b"Invoice Date,SKU,Units Sold\n2025-01-01,SKU-001,10\n2025-01-02,SKU-001,15\n"
    
    # 1. Suggest mapping
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    res = client.post("/api/suggest-mapping", data={"use_case": "demand_forecasting"}, files=files)
    assert res.status_code == 200
    mapping_data = res.json()
    assert "mapping" in mapping_data
    assert mapping_data["mapping"]["date"] == "Invoice Date"
    assert mapping_data["mapping"]["product_id"] == "SKU"
    assert mapping_data["mapping"]["qty"] == "Units Sold"

    # 2. Assess
    files2 = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    res2 = client.post(
        "/api/assess",
        data={
            "use_case": "demand_forecasting",
            "mapping": json.dumps(mapping_data["mapping"])
        },
        files=files2
    )
    assert res2.status_code == 200
    report = res2.json()
    assert "readiness" in report
    assert "verdict" in report
    assert "summary" in report
    assert "all_checks" in report
