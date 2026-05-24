from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.routers import questions, assess, report, ai_diagnosis, track, admin

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="亲子教育评估系统",
    description="基于40题标准化问卷的儿童亲子评估Web系统",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(assess.router)
app.include_router(report.router)
app.include_router(ai_diagnosis.router)
app.include_router(track.router)
app.include_router(admin.router)

app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/js", StaticFiles(directory="static/js"), name="js")
app.mount("/images", StaticFiles(directory="static/images"), name="images")


@app.get("/")
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/quiz")
async def quiz_page():
    with open("static/quiz.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/report")
async def report_page():
    with open("static/report.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
