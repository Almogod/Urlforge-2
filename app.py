import os
import time
import concurrent.futures
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# Core modules
from src.crawler_engine.crawler import crawl
from src.services.extractor import extract_metadata
from src.services.normalizer import normalize
from src.services.filter import is_valid
from src.services.generator import generate_sitemaps
from src.services.sitemap_parser import get_sitemap_urls
from src.engine.engine import run_engine
from src.automation.automation_engine import run_automation

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define or Import your config here
AUTOMATION_CONFIG = {
    "platform": "github",
    "github_token": os.getenv("GITHUB_TOKEN", "..."),
    "repo": "user/site-repo",
    "branch": "main"
}

progress_store = {}

@app.get("/progress")
def get_progress(task_id: str):
    return {"status": progress_store.get(task_id, "Starting..."), "progress": None}

def build_clean_urls(pages, fix_canonical=False):
    clean = set()
    for p in pages:
        meta = extract_metadata(p)
        if not is_valid(meta): continue
        chosen = meta["url"]
        if fix_canonical:
            canonical = meta.get("canonical")
            if canonical and canonical.startswith("http"): chosen = canonical
        chosen = chosen.split("?")[0]
        try:
            clean.add(normalize(chosen))
        except:
            continue
    return sorted(list(clean))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    domain: str = Form(...),
    limit: int = Form(50),
    use_js: bool = Form(False),
    fix_canonical: bool = Form(False),
    task_id: str = Form(None)
):
    try:
        if task_id: progress_store[task_id] = "Crawling website pages..."
        pages, graph = crawl(domain, limit=limit)
        
        if task_id: progress_store[task_id] = "Checking existing sitemap..."
        sitemap_urls = get_sitemap_urls(domain)
        for url in sitemap_urls:
            pages.append({"url": url, "status": 200, "html": ""})

        pages.sort(key=lambda x: x["url"])

        if task_id: progress_store[task_id] = "Cleaning URLs..."
        clean_urls = build_clean_urls(pages, fix_canonical)

        def engine_progress(msg):
            if task_id: progress_store[task_id] = msg

        # 1. Run Engine
        engine_result = run_engine(pages, clean_urls, domain, graph, progress_callback=engine_progress)

        # 2. Run Automation using the constant
        if task_id: progress_store[task_id] = "Running Automations..."
        actions = engine_result.get("actions", [])
        automation_result = run_automation(actions, AUTOMATION_CONFIG)

        # 3. Generate Files
        if task_id: progress_store[task_id] = "Finalizing..."
        fixed_urls = engine_result.get("fixed_urls", [])
        files = generate_sitemaps(fixed_urls, base_url=domain)

        # 4. Response
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "files": files,
                "count": len(clean_urls),
                "engine_result": engine_result,
                "automation_result": automation_result,
                # Mapping individual keys for existing template logic
                "audit": engine_result.get("audit"),
                "meta_issues": engine_result.get("modules", {}).get("meta", {}).get("issues", []),
                "meta_fixes": engine_result.get("modules", {}).get("meta", {}).get("fixes", {}),
                "link_issues": engine_result.get("modules", {}).get("internal_links", {}).get("issues", {}),
                "link_suggestions": engine_result.get("modules", {}).get("internal_links", {}).get("suggestions", {}),
                "plan": engine_result.get("plan"),
                "image_issues": engine_result.get("modules", {}).get("image_seo", {}).get("issues", []),
                "image_fixes": engine_result.get("modules", {}).get("image_seo", {}).get("fixes", {}),
                "core_issues": engine_result.get("modules", {}).get("core_web_vitals", {}).get("issues", []),
                "core_suggestions": engine_result.get("modules", {}).get("core_web_vitals", {}).get("suggestions", {}),
                "keyword_gap": engine_result.get("modules", {}).get("keyword_gap", {}).get("keyword_gap", {}),
                "site_keywords": engine_result.get("modules", {}).get("keyword_gap", {}).get("site_keywords", []),
                "competitor_keywords": engine_result.get("modules", {}).get("keyword_gap", {}).get("competitor_keywords", {}),
                "actions": actions,
                "strategy": engine_result.get("strategy", []),
                "seo_score": engine_result.get("seo_score", 0)
            }
        )

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})
    finally:
        if task_id and task_id in progress_store:
            del progress_store[task_id]

@app.get("/download")
def download_file(file: str):
    return FileResponse(os.path.abspath(file), filename=os.path.basename(file))
