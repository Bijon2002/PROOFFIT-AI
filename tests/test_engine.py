import pytest
import pandas as pd
import numpy as np
from app.core.templates import TEMPLATES
from app.services.engine import assess_dataset
from app.services.llm import heuristic_mapping

def test_templates_integrity():
    assert "demand_forecasting" in TEMPLATES
    assert "customer_churn" in TEMPLATES
    assert "fraud_detection" in TEMPLATES
    for uc, tpl in TEMPLATES.items():
        assert "required" in tpl
        assert len(tpl["required"]) > 0
        assert "weights" in tpl
        assert "blocker_below" in tpl

def test_demand_forecasting_assessment():
    dates = pd.date_range("2025-01-01", "2026-06-01", freq="D")
    rows = []
    for d in dates:
        rows.append({"Invoice Date": d.strftime("%Y-%m-%d"), "SKU": "P1", "Units Sold": 10})
    df = pd.DataFrame(rows)

    mapping = {"date": "Invoice Date", "product_id": "SKU", "qty": "Units Sold"}
    res = assess_dataset(df, "demand_forecasting", mapping)

    assert "readiness" in res
    assert 0 <= res["readiness"] <= 100
    assert res["verdict"] in ["Production Ready", "Needs Remediation", "Critical Blockers"]
    assert "all_checks" in res
    assert len(res["all_checks"]) >= 5
    assert "dataset_profile" in res

def test_heuristic_synonym_mapping():
    df = pd.DataFrame(columns=["Invoice Date", "item_code", "quantity_sold", "branch_id"])
    canonical = ["date", "product_id", "qty", "store_id"]
    mapped = heuristic_mapping(df, canonical)

    assert mapped["date"] == "Invoice Date"
    assert mapped["product_id"] == "item_code"
    assert mapped["qty"] == "quantity_sold"
    assert mapped["store_id"] == "branch_id"

def test_churn_assessment():
    df = pd.DataFrame({
        "Cust_ID": [f"C{i}" for i in range(100)],
        "Tenure": [12] * 100,
        "Monthly": [50.0] * 100,
        "Churned": ["Yes" if i % 4 == 0 else "No" for i in range(100)]
    })
    mapping = {
        "customer_id": "Cust_ID",
        "tenure_months": "Tenure",
        "monthly_charges": "Monthly",
        "churn_label": "Churned"
    }
    res = assess_dataset(df, "customer_churn", mapping)
    assert res["readiness"] > 0
    assert len(res["all_checks"]) >= 4
