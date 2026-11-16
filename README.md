<div align="center">

# 🛡️ PROOFFIT AI
### *Know your data before you trust your AI.*

**Enterprise Use-Case Data Readiness Assessment Engine**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[Live Demo](#quickstart) • [Architecture](#architecture) • [Supported AI Use Cases](#supported-ai-use-cases) • [API Docs](#api-reference) • [Privacy Guarantee](#privacy--security-guarantee)

---

</div>

## 📌 Executive Overview

Over **80% of Enterprise AI initiatives stall or fail in production** not because of algorithmic deficiencies, but because of **silent data unreadiness**: broken historical continuity, subtle target leakage, severe class imbalances, and stale telemetry feeds.

Standard data quality tools check syntactic schema validation (e.g. *is this integer non-null?*). **PROOFFIT AI checks mathematical AI readiness**: *does this dataset have the temporal depth, stability, and distribution required for a specific machine learning architecture?*

```
                       ┌─────────────────────────┐
                       │  Your Raw Data (CSV)   │
                       └────────────┬────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │              PROOFFIT AI READINESS ENGINE              │
       │                                                        │
       │  [1] Heuristic & LLM Schema Matcher (Privacy Masked)   │
       │  [2] Mathematical & Statistical Diagnostic Evaluator  │
       │  [3] Chief AI Officer Executive Explainer             │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │  Executive Scorecard (0-100) + Actionable Remediation  │
       └────────────────────────────────────────────────────────┘
```

---

## 💡 Core Philosophy

| Pillar | Principle | Implementation |
| :--- | :--- | :--- |
| **Code Measures** | Deterministic calculations only. Zero hallucination. | `app/services/engine.py` runs statistical checks, gap ratios, and covariance tests. |
| **LLM Interprets** | High-level synthesis for business decision-makers. | `app/services/llm.py` summarizes technical blockers into C-suite remediation steps. |
| **Humans Validate** | Total transparency and user control. | Explicit schema mapping confirmation before running diagnostic checks. |
| **Privacy First** | Zero raw row leakage. | LLMs only receive masked token patterns (`a` for text, `9` for digits). Raw data stays 100% local. |

---

## 🏗️ Architecture & Project Structure

PROOFFIT AI is engineered following clean enterprise modular design:

```
PROOFFIT-AI/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory, CORS, static routes, and lifespan
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Global settings & environment configurations
│   │   └── templates.py         # AI Use-Case templates, thresholds, and blocker weights
│   ├── services/
│   │   ├── __init__.py
│   │   ├── engine.py            # Diagnostic measurement engine (deterministic scoring)
│   │   └── llm.py               # AI mapping matcher & executive report synthesizer
│   └── api/
│       ├── __init__.py
│       ├── schemas.py           # Pydantic request/response schemas
│       └── routes.py            # REST API endpoints
├── static/
│   ├── index.html               # Responsive Single Page Application UI
│   ├── css/
│   │   └── styles.css           # Modern dark-mode glassmorphism styling
│   └── js/
│       └── app.js               # Reactive frontend controller & SVG gauge renderer
├── sample_data/
│   ├── sample_retail.csv        # Demand forecasting test dataset (8,764 records)
│   └── sample_churn.csv         # Customer churn test dataset (2,512 records)
├── tests/
│   ├── __init__.py
│   ├── test_engine.py           # Unit tests for statistical checks & templates
│   └── test_api.py              # End-to-end API integration tests
├── .gitignore                   # Comprehensive Python & IDE exclusion rules
├── app.py                       # Root backward-compatible server entrypoint
├── engine.py                    # Root backward-compatible engine entrypoint
├── llm.py                       # Root backward-compatible LLM entrypoint
├── gen_sample.py                # Synthetic dataset generator for instant testing
├── run.py                       # Single-command server launcher
└── requirements.txt             # Pinned enterprise dependencies
```

---

## 🎯 Supported AI Use Cases

PROOFFIT AI features built-in evaluation templates tailored to major enterprise machine learning tasks:

| Use Case | Canonical Schema | Critical Quality Checks | Blocker Threshold |
| :--- | :--- | :--- | :---: |
| **Demand & Sales Forecasting** | `date`, `product_id`, `qty` | • Field Completeness<br>• Temporal Deduplication<br>• History Depth (≥ 365 days)<br>• Continuity (max 10% gaps)<br>• Recency (≤ 30 days)<br>• Target Leakage | Score < 0.60 |
| **Customer Churn Prediction** | `customer_id`, `tenure_months`, `monthly_charges`, `churn_label` | • Entity Uniqueness<br>• Class Imbalance Protection<br>• Missing Attribute Ratio<br>• Post-Event Leakage Flag | Score < 0.60 |
| **Predictive Maintenance** | `timestamp`, `machine_id`, `sensor_reading`, `failure_label` | • Telemetry Stream Recency<br>• Multi-Machine Span<br>• Sensor Variance (dead sensor check)<br>• Failure Lead Time | Score < 0.60 |
| **Financial Fraud Detection** | `transaction_id`, `timestamp`, `amount`, `user_id`, `is_fraud` | • Transaction ID Collision<br>• Extreme Class Imbalance<br>• Minimum Positive Cases (≥ 50)<br>• Post-Dispute Leakage | Score < 0.60 |
| **LLM & RAG Corpus Readiness** | `document_id`, `text`, `category` | • Body Completeness<br>• Token/Length Sufficiency<br>• Content Deduplication (anti-dilution) | Score < 0.60 |

---

## 🖥️ Modern Enterprise UI Features

- **Dynamic Circular Radial Gauge**: Animated SVG progress indicator reflecting the unified 0–100 Readiness Score with color-coded operational state (Emerald = Production Ready, Amber = Needs Remediation, Crimson = Critical Blockers).
- **One-Click Pre-Built Sample Loaders**: Test immediately with pre-loaded realistic datasets (**Retail Demand** & **Customer Churn**) with zero file hunting.
- **Interactive Schema Alignment**: Side-by-side cards with confidence badges, auto-suggested matches, and column type chips.
- **In-Browser Dataset Preview**: View the first 5 records in an interactive table before executing diagnostics.
- **Actionable Remediation Cards**: Detailed statistical evidence accompanied by specific developer instructions to resolve pipeline bottlenecks.
- **Executive Export**: One-click **PDF / Print Export** and **JSON Audit Download** for regulatory and enterprise compliance archives.

---

## 🚀 Quickstart

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/Bijon2002/PROOFFIT-AI.git
cd "PROOFFIT-AI"

# Create virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Datasets

```bash
python gen_sample.py
```

### 3. (Optional) Set Anthropic API Key

PROOFFIT AI includes high-accuracy heuristic synonym matching by default. For enhanced natural-language column inference and bespoke C-level narrative generation, provide an API key:

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Linux / macOS
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 4. Launch Application

```bash
python run.py
```
Or with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

Open your browser to: **[http://localhost:8000](http://localhost:8000)**  
Interactive Swagger API documentation is available at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🧪 Testing & Quality Assurance

Run the comprehensive test suite:

```bash
pytest tests -v
```

All 8 tests validate template integrity, statistical calculations, edge-case sanitization, and API endpoints.

---

## 🔌 API Reference

### `GET /api/health`
Health check and system status.
```json
{
  "status": "healthy",
  "service": "PROOFFIT AI",
  "version": "1.0.0",
  "anthropic_connected": false
}
```

### `GET /api/use-cases`
Lists all available evaluation templates, canonical schemas, and required fields.

### `POST /api/suggest-mapping`
Accepts a CSV file upload and use case ID. Returns detected columns, suggested mappings, and first 5 rows preview.

### `POST /api/assess`
Accepts a CSV file, use case ID, and confirmed JSON mapping string. Computes readiness metrics, checks, blockers, and executive summary.

---

## 🛡️ Privacy & Security Guarantee

```
+-----------------------------------------------------------+
| PROOFFIT AI Security Isolation Fence                      |
|                                                           |
| [Raw CSV Dataset] ===> Local Python Engine Only           |
|                                                           |
| [Schema Headers]  \                                       |
| [Column Dtypes]    ===> PII Masking Tool ===> LLM Service |
| [Masked Samples]  /    (e.g. "a99-aaaa")                  |
+-----------------------------------------------------------+
```

1. **Zero Data Storage**: Uploaded datasets are evaluated strictly in-memory and immediately garbage collected.
2. **PII Sanitization**: Values sent for AI mapping suggestions are masked using regex (`[A-Za-z] -> 'a'`, `\d -> '9'`).
3. **No Row Leakage**: Raw row content is never passed to external LLM APIs.

---

## 🧩 Adding a Custom Use Case

To add a new AI use case, append an entry to `TEMPLATES` in `app/core/templates.py`:

```python
"lead_scoring": {
    "title": "B2B Sales Lead Scoring",
    "description": "Predict conversion likelihood for marketing inbound leads.",
    "icon": "target",
    "required": ["lead_id", "created_date", "lead_source", "converted"],
    "optional": ["industry", "company_size", "website_visits"],
    "target": "converted",
    "weights": {
        "completeness": 0.30,
        "uniqueness": 0.25,
        "class_balance": 0.25,
        "leakage": 0.20
    },
    "blocker_below": 0.60
}
```

Add any unique domain synonyms to `SYNONYMS` in `app/services/llm.py`. The engine and UI will automatically reflect the new use case!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
Built with precision for Data Scientists, ML Engineers, and AI Leaders.
</div>
