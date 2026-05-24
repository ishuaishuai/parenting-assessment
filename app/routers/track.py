from fastapi import APIRouter, Request

from app.models.schemas import TrackRequest
from app.database import track_event

router = APIRouter()


@router.post("/api/track")
async def track(body: TrackRequest, request: Request):
    client_host = request.client.host if request.client else None
    await track_event(
        event_type=body.event_type,
        age_band=body.age_band,
        session_id=body.session_id,
        ip=client_host,
    )
    return {"success": True}
