from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class UseCaseInfo(BaseModel):
    title: str
    description: str
    icon: str
    required: List[str]
    optional: List[str] = Field(default_factory=list)

class SuggestMappingResponse(BaseModel):
    columns: List[str]
    mapping: Dict[str, Optional[str]]
    preview: List[Dict[str, Any]]
    total_rows: int
    total_columns: int

class CheckItem(BaseModel):
    check: str
    label: str
    score: float
    status: str
    evidence: Dict[str, Any]
    fix: str

class DatasetProfile(BaseModel):
    total_rows: int
    total_columns: int
    missing_cells_pct: float
    memory_mb: float
    duplicate_rows_pct: float

class AssessmentResponse(BaseModel):
    readiness: int
    verdict: str
    verdict_badge: str
    confidence: str
    summary: str
    rows_analysed: int
    columns_analysed: int
    blockers: List[CheckItem]
    all_checks: List[CheckItem]
    dataset_profile: Optional[DatasetProfile] = None
