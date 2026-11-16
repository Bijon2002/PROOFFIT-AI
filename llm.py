"""PROOFFIT AI LLM Service Entrypoint.
Backward-compatible wrapper exposing suggest_mapping, explain, and helper functions.
"""
from app.services.llm import (
    suggest_mapping,
    explain_assessment as explain,
    profile_columns as profile_cols,
    heuristic_mapping as heuristic,
    SYNONYMS as SYN
)

__all__ = ["suggest_mapping", "explain", "profile_cols", "heuristic", "SYN"]
