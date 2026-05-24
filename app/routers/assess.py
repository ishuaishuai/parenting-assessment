import json
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import AssessRequest, ReportResponse
from app.services.question_bank import get_questions
from app.services.assessment_engine import generate_report
from app.database import save_report, track_event
from app.routers.report import cache_report

router = APIRouter()


@router.post("/api/assess", response_model=ReportResponse)
async def assess(request: Request, body: AssessRequest):
    questions = get_questions(body.age_band)
    if not questions:
        raise HTTPException(status_code=404, detail="该年龄段题库不存在")

    answers = {i: score for i, score in enumerate(body.answers)}
    report_data = generate_report(body.age_band, questions, answers)

    dim_scores_json = json.dumps(report_data.get("scores", {}), ensure_ascii=False)
    report_id = await save_report(
        age_band=body.age_band,
        overall_score=report_data.get("meta", {}).get("overall_score", 0),
        dim_scores_json=dim_scores_json,
        flag_count=report_data.get("risk_analysis", {}).get("risk_count", 0),
        has_ai=False,
    )

    report_data["meta"]["report_id"] = report_id
    cache_report(report_id, report_data)

    client_host = request.client.host if request.client else None
    await track_event(
        event_type="report_generated",
        age_band=body.age_band,
        ip=client_host,
    )

    return ReportResponse(**report_data)
