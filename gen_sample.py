"""Dataset Generator for PROOFFIT AI sample test scenarios:
1. sample_retail.csv: Messy headers, short history, gaps, and duplicate demand rows.
2. sample_churn.csv: Customer churn records with contract types, tenure, charges, and churn flags.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def generate_retail_sample():
    rng = np.random.default_rng(7)
    end = pd.Timestamp.today().normalize() - pd.Timedelta(days=3)
    rows = []
    for p in range(40):
        start = end - pd.Timedelta(days=int(rng.choice([120, 200, 420, 500], p=[.4, .3, .2, .1])))
        for d in pd.date_range(start, end):
            if rng.random() < 0.88:  # ~12% missing days
                rows.append((d.strftime("%Y-%m-%d"), f"SKU-{p:03d}", int(rng.integers(0, 25)), "Colombo-Main", round(float(rng.uniform(10.0, 95.0)), 2)))
    
    df = pd.DataFrame(rows, columns=["Invoice Date", "SKU", "Units Sold", "Branch", "Unit Price"])
    df = pd.concat([df, df.sample(frac=0.02, random_state=2)])   # duplicates
    df.loc[df.sample(frac=0.03, random_state=3).index, "Units Sold"] = None
    
    # Save to sample_data and root
    target_path = SAMPLE_DIR / "sample_retail.csv"
    df.to_csv(target_path, index=False)
    df.to_csv(Path(__file__).resolve().parent / "sample_retail.csv", index=False)
    print(f"Retail sample: {len(df):,} rows -> {target_path}")

def generate_churn_sample():
    rng = np.random.default_rng(42)
    n = 2500
    customer_ids = [f"CUST-{i:05d}" for i in range(1, n + 1)]
    tenure = rng.integers(1, 73, size=n)
    monthly = np.round(rng.uniform(20.0, 119.5, size=n), 2)
    contracts = rng.choice(["Month-to-month", "One year", "Two year"], size=n, p=[0.55, 0.25, 0.20])
    payment_methods = rng.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], size=n)
    total_charges = np.round(tenure * monthly + rng.normal(0, 15, size=n), 2)
    total_charges = np.maximum(total_charges, monthly)

    # Churn probability higher with month-to-month, high monthly charges, low tenure
    prob = 0.20 + 0.25 * (contracts == "Month-to-month") + 0.15 * (monthly > 70) - 0.20 * (tenure > 36)
    prob = np.clip(prob, 0.05, 0.85)
    churn = [("Yes" if rng.random() < p else "No") for p in prob]

    df = pd.DataFrame({
        "Customer ID": customer_ids,
        "Tenure Months": tenure,
        "Monthly Charges": monthly,
        "Total Charges": total_charges,
        "Contract": contracts,
        "Payment Method": payment_methods,
        "Churn Status": churn
    })

    # Introduce minor realistic defects (1% missing, a few duplicates)
    df.loc[df.sample(frac=0.015, random_state=10).index, "Total Charges"] = None
    df = pd.concat([df, df.sample(n=12, random_state=99)])

    target_path = SAMPLE_DIR / "sample_churn.csv"
    df.to_csv(target_path, index=False)
    print(f"Churn sample: {len(df):,} rows -> {target_path}")

if __name__ == "__main__":
    generate_retail_sample()
    generate_churn_sample()
