"""LLM layer for PROOFFIT AI.
Provides AI-assisted column mapping and executive plain-language assessments.
Security & Privacy Guarantee:
Only column headers, dtypes, and masked samples ever leave the machine. No raw customer records are ever exposed.
"""
import os
import re
import json
from typing import Dict, List, Any, Optional
import pandas as pd
from app.core.config import settings

SYNONYMS: Dict[str, List[str]] = {
    # Demand Forecasting
    "date": ["date", "day", "timestamp", "invoice_date", "sale_date", "order_date", "txn_date", "time", "datetime"],
    "product_id": ["product_id", "sku", "item_code", "item_id", "product", "item", "code", "part_number"],
    "qty": ["qty", "quantity", "units", "units_sold", "sold", "sales_qty", "volume", "demand"],
    "price": ["price", "unit_price", "rate", "cost", "selling_price", "amount"],
    "store_id": ["store_id", "shop_id", "branch", "outlet", "location", "store", "warehouse"],
    
    # Customer Churn
    "customer_id": ["customer_id", "client_id", "user_id", "cust_id", "account_id", "subscriber_id"],
    "tenure_months": ["tenure_months", "tenure", "months_active", "duration_months", "account_age", "subscription_length"],
    "monthly_charges": ["monthly_charges", "monthly_fee", "recurring_charge", "mrr", "spend_per_month", "monthly_bill"],
    "churn_label": ["churn_label", "churn", "churned", "is_churn", "exited", "status", "attrition", "cancelled"],
    
    # Predictive Maintenance
    "timestamp": ["timestamp", "event_time", "time", "datetime", "record_time", "date_time"],
    "machine_id": ["machine_id", "device_id", "asset_id", "equipment_id", "tool_id", "unit_id"],
    "sensor_reading": ["sensor_reading", "sensor_val", "vibration", "temp", "telemetry", "measurement", "sensor_1"],
    "failure_label": ["failure_label", "failure", "broken", "status", "is_failed", "error_flag", "fault"],
    
    # Fraud Detection
    "transaction_id": ["transaction_id", "txn_id", "trans_id", "order_id", "payment_id", "ref_no"],
    "amount": ["amount", "txn_amount", "value", "charge", "price", "trans_amt"],
    "user_id": ["user_id", "customer_id", "sender_id", "account_number", "card_id"],
    "is_fraud": ["is_fraud", "fraud", "fraud_label", "fraudulent", "is_suspicious", "target"],
    
    # RAG / LLM
    "document_id": ["document_id", "doc_id", "id", "file_id", "article_id", "chunk_id"],
    "text": ["text", "body", "content", "document", "article_text", "passage", "chunk"],
    "category": ["category", "topic", "tag", "label", "genre", "section", "class"]
}

def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")

def _mask_sample(val: Any) -> str:
    """Mask letters with 'a' and numbers with '9' to protect PII."""
    s = str(val)[:25]
    s = re.sub(r"[A-Za-z]", "a", s)
    s = re.sub(r"\d", "9", s)
    return s

def profile_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    return [
        {
            "name": str(col),
            "dtype": str(df[col].dtype),
            "samples": [_mask_sample(x) for x in df[col].dropna().head(3).tolist()]
        }
        for col in df.columns
    ]

def heuristic_mapping(df: pd.DataFrame, canonical_fields: List[str]) -> Dict[str, Optional[str]]:
    cols = list(df.columns)
    used = set()
    out = {}

    for k in canonical_fields:
        match = None
        syns = SYNONYMS.get(k, [k])
        
        # Exact match or normalized exact match first
        for col in cols:
            if col not in used and _normalize(col) in syns:
                match = col
                break
        
        # Substring / contains match
        if not match:
            for col in cols:
                norm_c = _normalize(col)
                if col not in used and any(s in norm_c or norm_c in s for s in syns):
                    match = col
                    break

        out[k] = match
        if match:
            used.add(match)

    return out

def suggest_mapping(df: pd.DataFrame, canonical_fields: List[str]) -> Dict[str, Optional[str]]:
    key = settings.ANTHROPIC_API_KEY
    if key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            prompt = (
                f"You are a data engineering mapping assistant. Match dataset columns to canonical schema fields: {canonical_fields}.\n"
                f"Columns and masked samples (PII sanitized): {json.dumps(profile_columns(df))}\n"
                f"Return ONLY valid JSON mapping each canonical field to the best matching dataset column name or null if no match exists.\n"
                f'Example: {{"date": "Invoice Date", "product_id": "SKU"}}'
            )
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = resp.content[0].text.strip()
            # Clean markdown codeblocks if returned
            if "```" in raw_text:
                raw_text = re.sub(r"^```[a-z]*\n", "", raw_text)
                raw_text = re.sub(r"\n```$", "", raw_text)
            parsed = json.loads(raw_text)
            return {
                k: (parsed.get(k) if parsed.get(k) in df.columns else None)
                for k in canonical_fields
            }
        except Exception:
            pass  # Fall back to heuristic rule matching seamlessly

    return heuristic_mapping(df, canonical_fields)

def explain_assessment(report: Dict[str, Any], use_case: str) -> str:
    """Generate concise, high-impact executive summary.
    Sends only statistical check results and scores; never raw customer data."""
    facts = {
        "readiness_score": report["readiness"],
        "verdict": report["verdict"],
        "confidence": report["confidence"],
        "blockers": [
            {"check": b["label"], "evidence": b["evidence"], "fix": b["fix"]}
            for b in report.get("blockers", [])
        ],
        "checks_passed": len([c for c in report.get("all_checks", []) if c["status"] == "pass"]),
        "total_checks": len(report.get("all_checks", []))
    }

    key = settings.ANTHROPIC_API_KEY
    if key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            prompt = (
                f"You are a Chief AI Officer briefing executive leadership on whether enterprise data is ready for '{use_case}'.\n"
                f"Findings summary: {json.dumps(facts)}\n"
                f"Provide a clear 3-sentence executive evaluation:\n"
                f"Sentence 1: Overall readiness score and readiness status.\n"
                f"Sentence 2: Primary bottleneck, risk, or data hygiene strength.\n"
                f"Sentence 3: Direct remediation action recommended before committing machine learning engineering resources.\n"
                f"Be professional, direct, and actionable. Do not speculate."
            )
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.content[0].text.strip()
        except Exception:
            pass

    # Built-in deterministic explainer
    uc_name = use_case.replace("_", " ").title()
    score = report["readiness"]
    blockers = report.get("blockers", [])

    if not blockers and score >= 80:
        return (
            f"The dataset demonstrates strong data hygiene with a readiness score of {score}/100 for {uc_name}. "
            f"All required canonical features satisfy enterprise training thresholds without critical leakage or gap risks. "
            f"Recommended Action: Proceed with model baseline experiments and feature engineering."
        )
    elif score >= 55:
        top_issues = ", ".join([b["label"] for b in blockers[:2]]) if blockers else "moderate data inconsistencies"
        return (
            f"The dataset achieved a readiness score of {score}/100 ({report['verdict']}) for {uc_name}. "
            f"Key optimization areas identified: {top_issues}. "
            f"Recommended Action: Remediate the flagged fields before training to avoid degraded model performance."
        )
    else:
        top_issues = ", ".join([b["label"] for b in blockers[:3]]) if blockers else "critical data deficiencies"
        return (
            f"The dataset is currently NOT ready for production AI modeling, scoring {score}/100. "
            f"Critical blockers detected in: {top_issues}. "
            f"Recommended Action: Prioritize data pipeline fixes and address missing historical or entity coverage before ML experimentation."
        )
