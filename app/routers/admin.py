from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.database import _get_pool

router = APIRouter()
settings = get_settings()


def _verify_password(password: Optional[str]):
    if password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="密码错误")


@router.get("/admin", response_class=HTMLResponse)
async def admin_page():
    try:
        with open("static/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="admin.html 不存在")


@router.get("/api/admin/stats")
async def admin_stats(password: Optional[str] = None):
    _verify_password(password)
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    pool = await _get_pool()
    async with pool.acquire() as conn:
        total_reports = await conn.fetchval("SELECT COUNT(*) FROM reports")
        total_events = await conn.fetchval("SELECT COUNT(*) FROM events")
        avg_score = await conn.fetchval("SELECT AVG(overall_score) FROM reports")
        ai_count = await conn.fetchval("SELECT COUNT(*) FROM reports WHERE has_ai = TRUE")
        today_reports = await conn.fetchval(
            "SELECT COUNT(*) FROM reports WHERE DATE(created_at) = $1", today_str
        )
        flag_reports = await conn.fetchval(
            "SELECT COUNT(*) FROM reports WHERE flag_count > 0"
        )
        total_pv = await conn.fetchval("SELECT COALESCE(SUM(pv), 0) FROM daily_stats")
        today_pv = await conn.fetchval(
            "SELECT COALESCE(pv, 0) FROM daily_stats WHERE date = $1", today_str
        )
        today_complete = await conn.fetchval(
            "SELECT COALESCE(quiz_complete, 0) FROM daily_stats WHERE date = $1", today_str
        )

        return {
            "total_reports": total_reports or 0,
            "total_events": total_events or 0,
            "avg_score": round(avg_score, 2) if avg_score else 0,
            "ai_count": ai_count or 0,
            "today_reports": today_reports or 0,
            "flag_reports": flag_reports or 0,
            "total_pv": total_pv or 0,
            "today_pv": today_pv or 0,
            "today_complete": today_complete or 0,
        }


@router.get("/api/admin/funnel")
async def admin_funnel(password: Optional[str] = None):
    _verify_password(password)
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM daily_stats ORDER BY date DESC LIMIT 30"
        )
        return {
            "funnel": [
                {
                    "date": row["date"],
                    "pv": row["pv"],
                    "quiz_start": row["quiz_start"],
                    "quiz_complete": row["quiz_complete"],
                    "report_gen": row["report_gen"],
                    "ai_diag": row["ai_diag"],
                    "pdf_down": row["pdf_down"],
                }
                for row in rows
            ]
        }


@router.get("/api/admin/dimensions")
async def admin_dimensions(password: Optional[str] = None):
    _verify_password(password)
    import json
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT dim_scores_json FROM reports ORDER BY created_at DESC LIMIT 100"
        )
        dim_totals = {}
        dim_counts = {}
        for row in rows:
            dim_json = row["dim_scores_json"]
            if not dim_json:
                continue
            try:
                scores = json.loads(dim_json)
            except Exception:
                continue
            for dim, score in scores.items():
                dim_totals[dim] = dim_totals.get(dim, 0) + score
                dim_counts[dim] = dim_counts.get(dim, 0) + 1
        return {
            "dimensions": [
                {"dim": d, "avg": round(dim_totals[d] / dim_counts[d], 2)}
                for d in dim_totals
            ]
        }


@router.get("/api/admin/high-risk")
async def admin_high_risk(password: Optional[str] = None):
    _verify_password(password)
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM reports WHERE flag_count > 0 ORDER BY created_at DESC LIMIT 50"
        )
        return {
            "high_risk": [
                {
                    "id": row["id"],
                    "age_band": row["age_band"],
                    "overall_score": row["overall_score"],
                    "flag_count": row["flag_count"],
                    "has_ai": bool(row["has_ai"]),
                    "created_at": row["created_at"].isoformat() if row["created_at"] else "",
                }
                for row in rows
            ]
        }
