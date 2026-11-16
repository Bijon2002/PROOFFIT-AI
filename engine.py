"""PROOFFIT AI Core Engine Entrypoint.
Backward-compatible wrapper exposing TEMPLATES and assess functions.
"""
from app.core.templates import TEMPLATES
from app.services.engine import (
    assess_dataset as assess,
    run_checks,
    calculate_score as score,
    _check
)

__all__ = ["TEMPLATES", "assess", "run_checks", "score", "_check"]

if __name__ == "__main__":
    import json
    import pandas as pd
    import numpy as np

    rng = np.random.default_rng(0)
    days = pd.date_range("2026-05-01", "2026-10-31")
    rows = [(d, f"P{p}", int(rng.integers(0, 20)), "x") for p in range(50) for d in days]
    df = pd.DataFrame(rows, columns=["sale_date", "sku", "units", "note"])
    df.loc[df.sample(frac=0.05, random_state=1).index, "units"] = None

    r = assess(df, "demand_forecasting", {"date": "sale_date", "product_id": "sku", "qty": "units"})
    print(json.dumps({k: r[k] for k in ("readiness", "verdict", "confidence")}, indent=2))
    for b in r["blockers"]:
        print("BLOCKER:", b["label"], b["score"], b["evidence"], "->", b["fix"])
