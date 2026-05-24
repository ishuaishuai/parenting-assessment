from typing import Dict
import os
import tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from app.services.report_generator import generate_html_report

router = APIRouter()

_report_cache: Dict[int, dict] = {}


def cache_report(report_id: int, data: dict) -> None:
    _report_cache[report_id] = data


@router.get("/api/report/{report_id}.html", response_class=HTMLResponse)
async def get_report_html(report_id: int):
    data = _report_cache.get(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="报告不存在或已过期")
    html = generate_html_report(data)
    return HTMLResponse(content=html)


@router.get("/api/report/{report_id}.pdf")
async def get_report_pdf(report_id: int):
    data = _report_cache.get(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="报告不存在或已过期")

    html = generate_html_report(data)

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(status_code=501, detail="PDF 生成服务暂不可用")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as hf:
        hf.write(html)
        html_path = hf.name

    pdf_path = html_path.replace(".html", ".pdf")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"file://{html_path}", wait_until="networkidle")
            await page.pdf(path=pdf_path, format="A4", print_background=True)
            await browser.close()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {exc}")
    finally:
        if os.path.exists(html_path):
            os.remove(html_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"report_{report_id}.pdf",
    )
