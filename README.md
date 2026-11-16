# PROOFFIT AI (MVP)
Know your data before you trust your AI. Use-case data readiness assessment.

## Run
    pip install -r requirements.txt
    python gen_sample.py              # makes sample_retail.csv
    export ANTHROPIC_API_KEY=...      # optional; without it, rule-based mapping is used
    uvicorn app:app --reload          # open http://localhost:8000

## Flow
Upload CSV -> pick use case -> confirm column mapping -> readiness report.

## Design rules
- Code measures (engine.py). LLM only suggests mappings and explains (llm.py). Humans confirm.
- LLM sees column names, dtypes and masked samples only, never full rows.
- Thresholds in engine.py TEMPLATES are assumptions. Tune them with pilot data.
- Not a legal compliance check.

## Add a use case
Add an entry to TEMPLATES in engine.py (required fields, history, weights). No other change needed
for checks that already exist.
"# PROOFFIT-AI" 
