import aiosqlite
from app.config import get_settings

settings = get_settings()

INIT_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    age_band TEXT,
    session_id TEXT,
    ip TEXT,
    ua TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age_band TEXT,
    overall_score REAL,
    dim_scores_json TEXT,
    flag_count INTEGER,
    has_ai BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


async def init_db():
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        await db.executescript(INIT_SQL)
        await db.commit()


async def track_event(event_type: str, age_band: str = None, session_id: str = None, ip: str = None, ua: str = None):
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO events (event_type, age_band, session_id, ip, ua) VALUES (?, ?, ?, ?, ?)",
            (event_type, age_band, session_id, ip, ua)
        )
        await db.commit()


async def save_report(age_band: str, overall_score: float, dim_scores_json: str, flag_count: int, has_ai: bool = False):
    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO reports (age_band, overall_score, dim_scores_json, flag_count, has_ai) VALUES (?, ?, ?, ?, ?)",
            (age_band, overall_score, dim_scores_json, flag_count, int(has_ai))
        )
        await db.commit()
        return cursor.lastrowid
