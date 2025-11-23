import asyncio
import json
import os
import traceback
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl

from extractor import PaperExtractor
from html_generator import HTMLGenerator
from semantic_scholar_scraper import SemanticScholarScraper

BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / "web"
ARTIFACT_DIR = BASE_DIR / "artifacts"
HTML_DIR = ARTIFACT_DIR / "html"
DEBUG_DIR = ARTIFACT_DIR / "debug"

for folder in (HTML_DIR, DEBUG_DIR):
    folder.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Scholar Scraper UI")

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
app.mount("/artifacts", StaticFiles(directory=ARTIFACT_DIR), name="artifacts")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (WEB_DIR / "index.html").read_text(encoding="utf-8")


class ScrapeRequest(BaseModel):
    profile_url: HttpUrl
    max_papers: int = Field(50, ge=1, le=1000)


jobs: Dict[str, Dict[str, Any]] = {}


def extract_author_id(profile_url: str) -> str:
    parsed = urllib.parse.urlparse(profile_url)
    path_parts = parsed.path.rstrip("/").split("/")
    if len(path_parts) >= 2 and path_parts[-1].isdigit():
        return path_parts[-1]
    raise ValueError(
        "Semantic Scholar profile URL must look like "
        "'https://www.semanticscholar.org/author/Name/ID'."
    )


@app.post("/api/scrape")
async def start_scrape(request: ScrapeRequest) -> Dict[str, str]:
    try:
        author_id = extract_author_id(str(request.profile_url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job_id = uuid.uuid4().hex
    jobs[job_id] = {
        "status": "queued",
        "message": "Request accepted",
        "stage": "",
        "percentage": 0,
        "result": None,
        "error": None,
    }

    asyncio.create_task(
        run_scrape_job(
            job_id=job_id,
            author_id=author_id,
            profile_url=str(request.profile_url),
            max_papers=request.max_papers,
        )
    )

    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
async def scrape_status(job_id: str) -> Dict[str, Any]:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def run_scrape_job(job_id: str, author_id: str, profile_url: str, max_papers: int) -> None:
    job = jobs[job_id]

    def progress_handler(stage: str, current: int, total: int, percentage: float) -> None:
        job["stage"] = stage
        percent_value = round(min(100.0, max(0.0, percentage)))
        job["percentage"] = percent_value
        job["message"] = f"{stage}… {percent_value}% complete"

    job["status"] = "running"
    job["message"] = "Fetching data…"
    job["percentage"] = 5

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    html_path = HTML_DIR / f"semantic_scholar_{author_id}_{timestamp}.html"
    debug_path = DEBUG_DIR / f"debug_{author_id}_{timestamp}.json"

    scraper = SemanticScholarScraper(
        api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
        max_papers=max_papers,
        verbose=False,
        collect_debug=True,
        progress_handler=progress_handler,
    )

    try:
        papers = await scraper.scrape_profile(author_id)
        if not papers:
            job["status"] = "failed"
            job["message"] = "No papers found for this author."
            job["percentage"] = 100
            return

        validated_papers = [PaperExtractor.validate_paper_data(paper) for paper in papers]
        html_content = HTMLGenerator.generate_html(validated_papers, author_id)
        html_path.write_text(html_content, encoding="utf-8")

        debug_report = scraper.build_debug_report(user_id=author_id)
        debug_path.write_text(json.dumps(debug_report, indent=2), encoding="utf-8")

        job["status"] = "completed"
        job["message"] = f"Scrape complete. Collected {len(validated_papers)} papers."
        job["percentage"] = 100
        job["stage"] = "Completed"
        job["result"] = {
            "author_id": author_id,
            "profile_url": profile_url,
            "total_papers": len(validated_papers),
            "html_url": f"/artifacts/html/{html_path.name}",
            "debug_url": f"/artifacts/debug/{debug_path.name}",
        }
    except Exception as exc:  # pylint: disable=broad-except
        traceback.print_exc()
        job["status"] = "failed"
        job["error"] = str(exc)
        job["message"] = "Scrape failed. Check server logs for details."
        job["percentage"] = 100

