import io
import json
import os
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.templates import TEMPLATES
from app.services.engine import assess_dataset
from app.services.llm import suggest_mapping, explain_assessment
from app.api.schemas import SuggestMappingResponse, AssessmentResponse

router = APIRouter(prefix="/api")

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"

def parse_csv_upload(file: UploadFile) -> pd.DataFrame:
    try:
        content = file.file.read()
        if len(content) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size ({settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB)"
            )
        # Try utf-8 first, fallback to latin-1
        try:
            return pd.read_csv(io.BytesIO(content), encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(content), encoding="latin-1")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "anthropic_connected": bool(settings.ANTHROPIC_API_KEY)
    }

@router.get("/use-cases")
def list_use_cases() -> Dict[str, Any]:
    return {
        key: {
            "title": val["title"],
            "description": val["description"],
            "icon": val.get("icon", "database"),
            "required": val["required"],
            "optional": val.get("optional", [])
        }
        for key, val in TEMPLATES.items()
    }

@router.get("/sample-datasets")
def list_sample_datasets():
    samples = []
    if SAMPLE_DATA_DIR.exists():
        for p in SAMPLE_DATA_DIR.glob("*.csv"):
            samples.append({
                "id": p.stem,
                "filename": p.name,
                "size_kb": round(p.stat().st_size / 1024, 1),
                "recommended_use_case": "demand_forecasting" if "retail" in p.name else "customer_churn" if "churn" in p.name else "demand_forecasting"
            })
    return {"samples": samples}

@router.get("/sample-data/{dataset_name}")
def get_sample_data(dataset_name: str):
    file_path = SAMPLE_DATA_DIR / f"{dataset_name}.csv"
    if not file_path.exists():
        # Check root as fallback
        root_path = Path(__file__).resolve().parent.parent.parent / f"{dataset_name}.csv"
        if root_path.exists():
            file_path = root_path
        else:
            raise HTTPException(status_code=404, detail="Sample dataset not found")
    return FileResponse(
        path=str(file_path),
        filename=f"{dataset_name}.csv",
        media_type="text/csv"
    )

@router.post("/suggest-mapping", response_model=SuggestMappingResponse)
def api_suggest_mapping(file: UploadFile = File(...), use_case: str = Form(...)):
    if use_case not in TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown AI use case '{use_case}'")

    df = parse_csv_upload(file)
    if len(df) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV contains zero data rows.")

    tpl = TEMPLATES[use_case]
    fields_to_map = tpl["required"] + tpl.get("optional", [])
    mapping = suggest_mapping(df, fields_to_map)

    # Format first 5 rows for UI table preview
    preview_df = df.head(5).fillna("null")
    preview = preview_df.to_dict(orient="records")

    return SuggestMappingResponse(
        columns=list(df.columns),
        mapping=mapping,
        preview=preview,
        total_rows=len(df),
        total_columns=len(df.columns)
    )

@router.post("/assess", response_model=AssessmentResponse)
def api_assess(
    file: UploadFile = File(...),
    use_case: str = Form(...),
    mapping: str = Form(...)
):
    if use_case not in TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown AI use case '{use_case}'")

    try:
        col_map = json.loads(mapping)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid mapping JSON format.")

    df = parse_csv_upload(file)
    tpl = TEMPLATES[use_case]

    # Validate all required fields have a mapped column that exists in CSV
    missing_fields = []
    for req in tpl["required"]:
        actual_col = col_map.get(req)
        if not actual_col or actual_col not in df.columns:
            missing_fields.append(req)

    if missing_fields:
        missing_str = ", ".join(missing_fields)
        raise HTTPException(
            status_code=400,
            detail=f"Please map the following required canonical fields before running assessment: {missing_str}"
        )

    # Filter out empty or null mappings
    clean_map = {k: v for k, v in col_map.items() if v and v in df.columns}

    # Run analytical engine
    report = assess_dataset(df, use_case, clean_map)

    # Generate LLM executive summary
    report["summary"] = explain_assessment(report, use_case)
    report["rows_analysed"] = len(df)
    report["columns_analysed"] = len(clean_map)

    return report
