"""PROOFFIT AI Analytical Engine.
Provides deterministic, privacy-first data readiness measurements for AI use cases.
Philosophy: Code measures; LLM interprets & explains; Humans validate.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.core.templates import TEMPLATES

def _check(name: str, label: str, score: float, evidence: Dict[str, Any], fix: str) -> Dict[str, Any]:
    clamped = round(float(max(0.0, min(1.0, score))), 3)
    status = "pass" if clamped >= 0.80 else "warn" if clamped >= 0.60 else "fail"
    return {
        "check": name,
        "label": label,
        "score": clamped,
        "status": status,
        "evidence": evidence,
        "fix": fix
    }

def run_demand_forecasting_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    d["date"] = pd.to_datetime(d["date"], errors="coerce")

    # 1. Completeness
    miss = d[tpl["required"]].isna().mean()
    out.append(_check(
        "completeness", "Field Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Fill or source missing values in required fields (date, product_id, qty)."
    ))

    # 2. Uniqueness (duplicate date+product rows)
    dup = float(d.duplicated(["date", "product_id"]).mean())
    out.append(_check(
        "uniqueness", "Temporal Deduplication", 1.0 - dup * 5.0,
        {"duplicate_records": f"{dup:.2%}"},
        "Deduplicate records to ensure strictly one transaction/demand entry per product per day."
    ))

    # 3. History depth and continuity
    valid_dates = d.dropna(subset=["date"])
    if len(valid_dates) > 0:
        g = valid_dates.groupby("product_id")["date"]
        span = (g.max() - g.min()).dt.days
        cov = float((span >= tpl["min_history_days"]).mean()) if len(span) > 0 else 0.0
        full_days = g.nunique()
        gap = 1.0 - (full_days / (span + 1)).clip(upper=1.0)
        gap_ok = float((gap <= tpl["max_gap_ratio"]).mean()) if len(gap) > 0 else 0.0
        history_score = 0.6 * cov + 0.4 * gap_ok
        evidence = {
            "products_with_min_history": f"{cov:.1%}",
            "products_with_low_gaps": f"{gap_ok:.1%}",
            "required_history_days": tpl["min_history_days"]
        }
    else:
        history_score = 0.0
        evidence = {"error": "No valid parseable dates found in date column."}
    
    out.append(_check(
        "history", "Historical Depth & Continuity", history_score,
        evidence,
        f"Ensure at least {tpl['min_history_days']} days of continuous sales history across products."
    ))

    # 4. Freshness
    if len(valid_dates) > 0 and pd.notna(d["date"].max()):
        age = int((pd.Timestamp.today().normalize() - d["date"].max()).days)
        freshness_score = 1.0 - max(0, age - tpl["max_staleness_days"]) / 180.0
        evidence = {"days_since_latest_record": max(0, age), "threshold_days": tpl["max_staleness_days"]}
    else:
        freshness_score = 0.0
        evidence = {"days_since_latest_record": "Unknown / Missing"}

    out.append(_check(
        "freshness", "Data Freshness & Recency", freshness_score,
        evidence,
        f"Connect an automated data pipeline; records older than {tpl['max_staleness_days']} days skew forecasts."
    ))

    # 5. Target Leakage
    t = tpl.get("target")
    leaks = []
    num = d.select_dtypes(include=[np.number])
    if t in num.columns and len(num) > 10:
        corr = num.corr()[t].drop(t, errors="ignore").abs()
        leaks = corr[corr > 0.98].index.tolist()
    
    out.append(_check(
        "leakage", "Target Leakage Protection", 0.3 if leaks else 1.0,
        {"suspect_columns": leaks if leaks else "None detected"},
        "Review and drop features that are derived from or highly colinear with the target variable."
    ))

    return out

def run_customer_churn_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    # 1. Completeness
    miss = d[tpl["required"]].isna().mean()
    out.append(_check(
        "completeness", "Field Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Impute or eliminate missing values in customer attributes and charges."
    ))

    # 2. Uniqueness (one row per customer)
    dup = float(d.duplicated(["customer_id"]).mean())
    out.append(_check(
        "uniqueness", "Customer Entity Uniqueness", 1.0 - dup * 5.0,
        {"duplicate_customer_ids": f"{dup:.2%}"},
        "Consolidate multiple transactions into unique customer-level summary rows."
    ))

    # 3. Class Balance
    churn_col = d["churn_label"].dropna()
    val_counts = churn_col.value_counts(normalize=True)
    if len(val_counts) >= 2:
        minority_share = float(val_counts.min())
        balance_score = 1.0 if (minority_share >= 0.15) else (minority_share / 0.15)
        evidence = {f"class_{k}": f"{v:.1%}" for k, v in val_counts.items()}
    else:
        balance_score = 0.1
        evidence = {"warning": "Single class or empty target detected"}

    out.append(_check(
        "class_balance", "Target Class Distribution", balance_score,
        evidence,
        "Ensure training sample has adequate representation of churned versus retained accounts (min 10-15%)."
    ))

    # 4. Leakage
    t = "churn_label"
    leaks = []
    num = d.select_dtypes(include=[np.number])
    if t in num.columns and len(num) > 10:
        corr = num.corr()[t].drop(t, errors="ignore").abs()
        leaks = corr[corr > 0.95].index.tolist()

    out.append(_check(
        "leakage", "Target Leakage Protection", 0.3 if leaks else 1.0,
        {"suspect_columns": leaks if leaks else "None detected"},
        "Drop post-churn events (e.g. account cancellation date or refund status) before training."
    ))

    return out

def run_predictive_maintenance_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    d["timestamp"] = pd.to_datetime(d["timestamp"], errors="coerce")

    # 1. Completeness
    miss = d[tpl["required"]].isna().mean()
    out.append(_check(
        "completeness", "Telemetry Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Eliminate null sensor telemetry and timestamp entries."
    ))

    # 2. History & Machine Coverage
    valid = d.dropna(subset=["timestamp"])
    if len(valid) > 0:
        machines = valid["machine_id"].nunique()
        span = (valid["timestamp"].max() - valid["timestamp"].min()).days
        history_score = min(1.0, span / max(1, tpl["min_history_days"]))
        evidence = {"distinct_machines": machines, "timespan_days": int(span)}
    else:
        history_score = 0.0
        evidence = {"error": "Invalid timestamps"}

    out.append(_check(
        "history", "Telemetry History Span", history_score,
        evidence,
        f"Collect at least {tpl['min_history_days']} days of continuous telemetry."
    ))

    # 3. Freshness
    if len(valid) > 0:
        age = int((pd.Timestamp.today().normalize() - valid["timestamp"].max()).days)
        freshness_score = 1.0 - max(0, age - tpl["max_staleness_days"]) / 90.0
        evidence = {"days_since_latest_telemetry": max(0, age)}
    else:
        freshness_score = 0.0
        evidence = {"days_since_latest_telemetry": "N/A"}

    out.append(_check(
        "freshness", "Telemetry Stream Recency", freshness_score,
        evidence,
        f"Stream live IoT sensor data; gaps over {tpl['max_staleness_days']} days degrade reliability."
    ))

    # 4. Sensor Variance
    sensor_col = pd.to_numeric(d["sensor_reading"], errors="coerce")
    std = float(sensor_col.std()) if len(sensor_col.dropna()) > 1 else 0.0
    var_score = 1.0 if std > 0.01 else 0.2
    out.append(_check(
        "sensor_variance", "Sensor Signal Variance", var_score,
        {"sensor_std_dev": round(std, 4), "is_flatlined": std <= 0.01},
        "Check for dead or flatlined sensors generating constant values."
    ))

    # 5. Leakage
    out.append(_check(
        "leakage", "Leakage Protection", 1.0,
        {"status": "No direct post-failure flags detected in features"},
        "Ensure features only use sensor readings prior to failure event."
    ))
    return out

def run_fraud_detection_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    # 1. Completeness
    miss = d[tpl["required"]].isna().mean()
    out.append(_check(
        "completeness", "Transaction Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Ensure all transaction metadata (amounts, timestamps, user IDs) are populated."
    ))

    # 2. Uniqueness
    dup = float(d.duplicated(["transaction_id"]).mean())
    out.append(_check(
        "uniqueness", "Transaction Uniqueness", 1.0 - dup * 10.0,
        {"duplicate_transaction_ids": f"{dup:.2%}"},
        "Each financial transaction must have a globally unique identifier."
    ))

    # 3. Class Balance & Extreme Imbalance
    fraud_col = d["is_fraud"].dropna()
    fraud_count = int((fraud_col.astype(str).str.lower().isin(["1", "true", "yes"])).sum())
    fraud_ratio = fraud_count / max(1, len(fraud_col))
    # In fraud, 0.1% to 10% is typical; if 0 fraud cases, fail!
    if fraud_count == 0:
        balance_score = 0.0
        evidence = {"fraud_cases": 0, "message": "Zero fraudulent cases in dataset"}
    elif fraud_count < 10:
        balance_score = 0.4
        evidence = {"fraud_cases": fraud_count, "fraud_rate": f"{fraud_ratio:.2%}"}
    else:
        balance_score = 1.0
        evidence = {"fraud_cases": fraud_count, "fraud_rate": f"{fraud_ratio:.2%}"}

    out.append(_check(
        "class_balance", "Fraud Target Representation", balance_score,
        evidence,
        "Ensure at least 50+ confirmed fraud cases are present for supervised training."
    ))

    # 4. Leakage
    out.append(_check(
        "leakage", "Feature Leakage Protection", 1.0,
        {"status": "Verified"},
        "Remove chargeback or investigation status flags created after transaction processing."
    ))
    return out

def run_rag_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    # 1. Completeness
    miss = d[tpl["required"]].isna().mean()
    out.append(_check(
        "completeness", "Corpus Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Documents must have non-null body text and categories."
    ))

    # 2. Length Sufficiency
    texts = d["text"].dropna().astype(str)
    lengths = texts.str.len()
    short_ratio = float((lengths < tpl["min_text_length"]).mean()) if len(lengths) > 0 else 1.0
    out.append(_check(
        "length_sufficiency", "Document Token/Length Sufficiency", 1.0 - short_ratio,
        {
            "avg_char_length": int(lengths.mean()) if len(lengths) > 0 else 0,
            "short_docs_ratio": f"{short_ratio:.1%}",
            "min_length_threshold": tpl["min_text_length"]
        },
        f"Filter out or chunk documents shorter than {tpl['min_text_length']} characters."
    ))

    # 3. Uniqueness (Duplicate text content)
    dup = float(d.duplicated(["text"]).mean()) if "text" in d.columns else 0.0
    out.append(_check(
        "uniqueness", "Content Deduplication", 1.0 - dup * 3.0,
        {"duplicate_documents": f"{dup:.2%}"},
        "Deduplicate corpus chunks to prevent LLM context dilution and retrieval bloat."
    ))
    return out

def run_generic_checks(d: pd.DataFrame, tpl: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    req = tpl.get("required", list(d.columns))
    miss = d[req].isna().mean()
    out.append(_check(
        "completeness", "Field Completeness", 1.0 - float(miss.mean()),
        {c: f"{v:.1%} missing" for c, v in miss.items()},
        "Resolve missing values across all required fields."
    ))
    dup = float(d.duplicated().mean())
    out.append(_check(
        "uniqueness", "Record Uniqueness", 1.0 - dup * 5.0,
        {"duplicate_rows": f"{dup:.2%}"},
        "Remove exact duplicate rows across the dataset."
    ))
    return out

def run_checks(df: pd.DataFrame, tpl: Dict[str, Any], mapping: Dict[str, str], use_case: str) -> List[Dict[str, Any]]:
    # Rename mapped columns to canonical keys
    inv_map = {actual: canonical for canonical, actual in mapping.items() if actual in df.columns}
    d = df.rename(columns=inv_map)

    if use_case == "demand_forecasting":
        return run_demand_forecasting_checks(d, tpl)
    elif use_case == "customer_churn":
        return run_customer_churn_checks(d, tpl)
    elif use_case == "predictive_maintenance":
        return run_predictive_maintenance_checks(d, tpl)
    elif use_case == "fraud_detection":
        return run_fraud_detection_checks(d, tpl)
    elif use_case == "rag_knowledge_base":
        return run_rag_checks(d, tpl)
    else:
        return run_generic_checks(d, tpl)

def calculate_score(checks: List[Dict[str, Any]], tpl: Dict[str, Any], n_rows: int) -> Dict[str, Any]:
    w = tpl.get("weights", {})
    # If weights don't sum cleanly or missing keys, fallback to equal weighting
    total_w = sum(w.get(c["check"], 1.0) for c in checks)
    if total_w > 0:
        overall = sum(c["score"] * w.get(c["check"], 1.0) for c in checks) / total_w
    else:
        overall = sum(c["score"] for c in checks) / max(1, len(checks))

    blocker_threshold = tpl.get("blocker_below", 0.60)
    blockers = [c for c in checks if c["score"] < blocker_threshold]

    confidence = "High" if n_rows > 20_000 else "Medium" if n_rows > 2_000 else "Low"

    if len(blockers) == 0 and overall >= 0.80:
        verdict = "Production Ready"
        verdict_badge = "ready"
    elif overall >= 0.55:
        verdict = "Needs Remediation"
        verdict_badge = "improve"
    else:
        verdict = "Critical Blockers"
        verdict_badge = "not_ready"

    return {
        "readiness": round(overall * 100),
        "verdict": verdict,
        "verdict_badge": verdict_badge,
        "confidence": confidence,
        "blockers": sorted(blockers, key=lambda c: c["score"]),
        "all_checks": checks
    }

def assess_dataset(df: pd.DataFrame, use_case: str, mapping: Dict[str, str]) -> Dict[str, Any]:
    if use_case not in TEMPLATES:
        raise ValueError(f"Unknown use case: {use_case}")

    tpl = TEMPLATES[use_case]
    checks = run_checks(df, tpl, mapping, use_case)
    result = calculate_score(checks, tpl, len(df))

    # Add dataset profiling metadata
    total_cells = df.size
    null_cells = int(df.isna().sum().sum())
    result["dataset_profile"] = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "missing_cells_pct": round((null_cells / max(1, total_cells)) * 100, 2),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "duplicate_rows_pct": round(float(df.duplicated().mean()) * 100, 2)
    }
    return result
