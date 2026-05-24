from fastapi import APIRouter, HTTPException

from app.models.schemas import AIDiagnosisRequest, AIDiagnosisResponse
from app.config import get_settings
from app.services.ai_client import (
    get_model_client,
    build_diagnosis_prompt,
    SYSTEM_PROMPT,
)

router = APIRouter()
settings = get_settings()


@router.post("/api/ai-diagnosis", response_model=AIDiagnosisResponse)
async def ai_diagnosis(body: AIDiagnosisRequest):
    if not settings.ENABLE_AI_DIAGNOSIS:
        raise HTTPException(status_code=403, detail="AI 诊断功能已禁用")
    if not settings.MODEL_API_KEY:
        raise HTTPException(status_code=503, detail="AI 服务未配置")

    client = get_model_client()
    prompt = build_diagnosis_prompt(body.report_data)

    try:
        content = await client.generate(prompt, system_prompt=SYSTEM_PROMPT)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI 服务调用失败: {exc}")

    return AIDiagnosisResponse(
        content=content,
        model_used=settings.MODEL_NAME,
        tokens_used=0,
    )
