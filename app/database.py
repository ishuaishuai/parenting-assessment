import asyncpg
from datetime import datetime
from app.config import get_settings

settings = get_settings()
_pool = None

INIT_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    age_band TEXT,
    session_id TEXT,
    ip TEXT,
    ua TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    age_band TEXT,
    overall_score REAL,
    dim_scores_json TEXT,
    flag_count INTEGER,
    has_ai BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_stats (
    date TEXT PRIMARY KEY,
    pv INTEGER DEFAULT 0,
    quiz_start INTEGER DEFAULT 0,
    quiz_complete INTEGER DEFAULT 0,
    report_gen INTEGER DEFAULT 0,
    ai_diag INTEGER DEFAULT 0,
    pdf_down INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(created_at);
"""


async def _get_pool():
    global _pool
    if _pool is None:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        _pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=10)
    return _pool


async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(INIT_SQL)


async def track_event(event_type: str, age_band: str = None, session_id: str = None, ip: str = None, ua: str = None):
    today = datetime.now().strftime("%Y-%m-%d")
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO events (event_type, age_band, session_id, ip, ua) VALUES ($1, $2, $3, $4, $5)",
            event_type, age_band, session_id, ip, ua
        )
        col_map = {
            'page_view': 'pv',
            'quiz_start': 'quiz_start',
            'quiz_complete': 'quiz_complete',
            'report_generated': 'report_gen',
            'ai_diagnosis': 'ai_diag',
            'pdf_download': 'pdf_down',
        }
        col = col_map.get(event_type)
        if col:
            await conn.execute(
                f"INSERT INTO daily_stats (date, {col}) VALUES ($1, 1) "
                f"ON CONFLICT(date) DO UPDATE SET {col} = daily_stats.{col} + 1",
                today
            )


async def save_report(age_band: str, overall_score: float, dim_scores_json: str, flag_count: int, has_ai: bool = False):
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO reports (age_band, overall_score, dim_scores_json, flag_count, has_ai) "
            "VALUES ($1, $2, $3, $4, $5) RETURNING id",
            age_band, overall_score, dim_scores_json, flag_count, has_ai
        )
        return row['id']
