import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_questions_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/questions/7-8")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 40
    assert len(data["questions"]) == 40


@pytest.mark.asyncio
async def test_assess_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/assess", json={
            "age_band": "7-8",
            "answers": [4] * 40
        })
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["meta"]["overall_score"] <= 100
    assert len(data["scores"]) == 5
    assert "dimension_analysis" in data
