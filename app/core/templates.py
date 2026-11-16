"""Use-case templates defining what 'ready' means for various enterprise AI tasks.
Each template includes canonical field expectations, baseline thresholds, weights, and blocker rules.
"""

TEMPLATES = {
    "demand_forecasting": {
        "title": "Demand & Sales Forecasting",
        "description": "Predict future product sales volume or inventory demand across temporal sales records.",
        "icon": "trending-up",
        "required": ["date", "product_id", "qty"],
        "optional": ["price", "store_id"],
        "min_history_days": 365,
        "min_product_coverage": 0.80,   # Share of products with enough historical span
        "max_gap_ratio": 0.10,          # Missing days inside recorded history
        "max_staleness_days": 30,
        "target": "qty",
        "weights": {
            "completeness": 0.25,
            "uniqueness": 0.15,
            "history": 0.25,
            "freshness": 0.15,
            "leakage": 0.20
        },
        "blocker_below": 0.60
    },
    "customer_churn": {
        "title": "Customer Churn Prediction",
        "description": "Predict likelihood of customer attrition to execute proactive retention campaigns.",
        "icon": "users",
        "required": ["customer_id", "tenure_months", "monthly_charges", "churn_label"],
        "optional": ["contract_type", "payment_method", "total_charges"],
        "min_rows": 500,
        "min_class_ratio": 0.05,        # At least 5% minority class
        "max_class_ratio": 0.95,        # At most 95% majority class
        "target": "churn_label",
        "weights": {
            "completeness": 0.30,
            "uniqueness": 0.20,
            "class_balance": 0.25,
            "leakage": 0.25
        },
        "blocker_below": 0.60
    },
    "predictive_maintenance": {
        "title": "Predictive Equipment Maintenance",
        "description": "Anticipate industrial machine failures from telemetry sensor streams before downtime occurs.",
        "icon": "cpu",
        "required": ["timestamp", "machine_id", "sensor_reading", "failure_label"],
        "optional": ["operating_hours", "temperature", "vibration"],
        "min_history_days": 60,
        "max_staleness_days": 14,
        "target": "failure_label",
        "weights": {
            "completeness": 0.25,
            "history": 0.25,
            "freshness": 0.20,
            "sensor_variance": 0.15,
            "leakage": 0.15
        },
        "blocker_below": 0.60
    },
    "fraud_detection": {
        "title": "Financial Fraud & Risk Detection",
        "description": "Detect anomalous or fraudulent financial transactions in real-time or batch.",
        "icon": "shield-alert",
        "required": ["transaction_id", "timestamp", "amount", "user_id", "is_fraud"],
        "optional": ["merchant_id", "country_code", "ip_address"],
        "min_rows": 1000,
        "max_staleness_days": 45,
        "target": "is_fraud",
        "weights": {
            "completeness": 0.25,
            "uniqueness": 0.25,
            "class_balance": 0.25,
            "leakage": 0.25
        },
        "blocker_below": 0.60
    },
    "rag_knowledge_base": {
        "title": "LLM Fine-Tuning & RAG Corpus",
        "description": "Evaluate text corpora readiness for LLM embeddings, Retrieval-Augmented Generation, or fine-tuning.",
        "icon": "sparkles",
        "required": ["document_id", "text", "category"],
        "optional": ["author", "created_at", "source_url"],
        "min_text_length": 50,          # Minimum characters per document
        "max_empty_ratio": 0.05,
        "target": "text",
        "weights": {
            "completeness": 0.35,
            "length_sufficiency": 0.35,
            "uniqueness": 0.30
        },
        "blocker_below": 0.60
    }
}
