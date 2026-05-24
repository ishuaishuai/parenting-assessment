from fastapi import APIRouter, HTTPException

from app.models.schemas import QuestionListResponse
from app.services.question_bank import get_questions, DIM_OPTIONS

router = APIRouter()


@router.get("/api/questions/{age_band}", response_model=QuestionListResponse)
async def get_questions_by_age_band(age_band: str):
    questions = get_questions(age_band)
    if not questions:
        raise HTTPException(status_code=404, detail="该年龄段题库不存在")
    return QuestionListResponse(
        age_band=age_band,
        total=len(questions),
        questions=questions,
    )
