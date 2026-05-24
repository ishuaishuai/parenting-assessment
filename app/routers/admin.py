from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
import aiosqlite

from app.config import get_settings
from app.database import INIT_SQL

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
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        total_reports = await db.execute_fetchall("SELECT COUNT(*) FROM reports")
        total_events = await db.execute_fetchall("SELECT COUNT(*) FROM events")
        avg_score = await db.execute_fetchall(
            "SELECT AVG(overall_score) FROM reports"
        )
        ai_count = await db.execute_fetchall(
            "SELECT COUNT(*) FROM reports WHERE has_ai = 1"
        )
        today_reports = await db.execute_fetchall(
            "SELECT COUNT(*) FROM reports WHERE DATE(created_at) = ?", (today_str,)
        )
        flag_reports = await db.execute_fetchall(
            "SELECT COUNT(*) FROM reports WHERE flag_count > 0"
        )
        total_pv = await db.execute_fetchall("SELECT SUM(pv) FROM daily_stats")
        today_pv = await db.execute_fetchall(
            "SELECT pv FROM daily_stats WHERE date = ?", (today_str,)
        )
        today_complete = await db.execute_fetchall(
            "SELECT quiz_complete FROM daily_stats WHERE date = ?", (today_str,)
        )

        return {
            "total_reports": total_reports[0][0] if total_reports else 0,
            "total_events": total_events[0][0] if total_events else 0,
            "avg_score": round(avg_score[0][0], 2) if avg_score and avg_score[0][0] else 0,
            "ai_count": ai_count[0][0] if ai_count else 0,
            "today_reports": today_reports[0][0] if today_reports else 0,
            "flag_reports": flag_reports[0][0] if flag_reports else 0,
            "total_pv": total_pv[0][0] if total_pv and total_pv[0][0] else 0,
            "today_pv": today_pv[0][0] if today_pv and today_pv[0][0] else 0,
            "today_complete": today_complete[0][0] if today_complete and today_complete[0][0] else 0,
        }


@router.get("/api/admin/funnel")
async def admin_funnel(password: Optional[str] = None):
    _verify_password(password)
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
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
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        rows = await db.execute_fetchall(
            "SELECT dim_scores_json FROM reports ORDER BY created_at DESC LIMIT 100"
        )
        dim_totals = {}
        dim_counts = {}
        for (dim_json,) in rows:
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
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
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
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        }
