from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class Question(BaseModel):
    id: str
    dim: str
    text: str
    options: List[str]
    band: str
    red_flag: bool = False
    critical: bool = False


class QuestionListResponse(BaseModel):
    age_band: str
    total: int
    questions: List[Question]


class AssessRequest(BaseModel):
    age_band: str
    answers: List[int]


class DimensionAnalysis(BaseModel):
    dim_code: str
    dim_name: str
    score: float
    level: str
    level_code: str
    interpretation: str
    strengths: List[str]
    concerns: List[str]
    development_tips: List[str]
    scripts: List[str]
    reflections: List[str]


class PriorityActions(BaseModel):
    immediate: List[str]
    short_term: List[str]
    long_term: List[str]
    resources: List[str]


class ReportResponse(BaseModel):
    meta: Dict[str, Any]
    summary: str
    scores: Dict[str, float]
    dimension_analysis: Dict[str, DimensionAnalysis]
    risk_analysis: Dict[str, Any]
    cross_analysis: str
    priority_actions: PriorityActions
    environment: str
    flags: List[Dict[str, Any]]
    diagnosis_links: List[Dict[str, Any]]


class AIDiagnosisRequest(BaseModel):
    report_data: Dict[str, Any]
    focus_dim: Optional[str] = None


class AIDiagnosisResponse(BaseModel):
    content: str
    model_used: str
    tokens_used: int = 0


class TrackRequest(BaseModel):
    event_type: str
    age_band: Optional[str] = None
    session_id: Optional[str] = None
