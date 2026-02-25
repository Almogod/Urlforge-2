from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

from src.crawler import crawl
from src.js_crawler import crawl_js_sync
from src.extractor import extract_metadata
from src.normalizer import normalize
from src.filter import is_valid
from src.generator import generate_sitemaps

# Initialize app first so decorators work
app = FastAPI()

# Mount the current directory to serve generated XML files
app.mount("/files", StaticFiles(directory="."), name="files")

templates = Jinja2Templates(directory="templates")

@app.get("/download/{filename}")
def download_file(filename: str):
    return FileResponse(path=filename, filename=filename)

def build_clean_urls(pages, fix_canonical=False):
    clean = set()
    for p in pages:
        meta = extract_metadata(p)
        if not is_valid(meta):
            continue
        chosen = meta["canonical"] if fix_canonical else meta["url"]
        clean.add(normalize(chosen))
    return list(clean)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
def generate(
    request: Request, 
    domain: str = Form(...), 
    limit: int = Form(200), 
    use_js: bool = Form(False),
    fix_canonical: bool = Form(False)
):
    if use_js:
        pages = crawl_js_sync(domain, limit=limit)
    else:
        pages = crawl(domain, limit=limit)

    clean_urls = build_clean_urls(pages, fix_canonical)
    files = generate_sitemaps(clean_urls, base_url=domain)

    # Added requested print statements
    print(f"Crawled pages: {len(pages)}")
    print(f"Clean URLs: {len(clean_urls)}")
    print(f"Generated files: {files}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "files": files,
        "count": len(clean_urls)
    })
