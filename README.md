# 🔗 UrlForger

A production-grade FastAPI web tool for crawling AI-generated websites, auditing URL integrity, running deep SEO analysis, and generating valid XML sitemaps — all from a clean browser UI.

---

## Table of Contents

- [Why It Exists](#why-it-exists)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Security](#security)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [SEO Modules](#seo-modules)
- [Use Cases](#use-cases)
- [Repository Structure](#repository-structure)

---

## What It Exists

AI-generated websites are fast to build but technically fragile. Common problems include broken internal links, malformed URLs, missing meta tags, no sitemap, and poor heading hierarchy — all of which silently hurt SEO and search indexing. UrlForger automates the full remediation pipeline: crawl → validate → audit → report → generate sitemap.

---

## Architecture

```
Browser UI (Jinja2)
       │
  FastAPI (app.py)
  ├── router_tasks     → task polling
  ├── router_crawl     → crawl & audit
  └── router_plugin    → approval-gated workflow
       │
  Core Services
  ├── crawler.py       (Playwright / Chromium)
  ├── seo_engine.py    (11 analysis modules)
  └── task_store.py    (in-memory or Redis)
       │
  Middleware
  └── Rate limiting · Security headers · Sentry · Prometheus · CORS
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| Templating | Jinja2 |
| Browser automation | Playwright (Chromium) |
| HTML parsing | BeautifulSoup4 + lxml |
| Rate limiting | slowapi |
| Metrics | prometheus-fastapi-instrumentator |
| Error tracking | sentry-sdk |
| Task persistence | Redis (or in-memory) |
| Data validation | Pydantic v2 |
| Config | pydantic-settings |
| Database | SQLAlchemy + Alembic |
| Container | Docker (multi-stage) |
| Testing | pytest |

---

## Core Features

### Web Crawler
Uses Playwright with headless Chromium to discover all pages — including JavaScript-rendered content. Respects `robots.txt`, deduplicates URLs, stays same-domain, and runs fully async. Each crawl is dispatched as a background task, returning a `task_id` immediately.

### URL Validation & Normalization
Every discovered URL is passed through a pipeline: scheme check → domain validation (via `tldextract`) → path normalization (resolve `../`, strip trailing index files, lowercase host) → HTTP probe to classify 200s, 404s, redirects, and errors.

### SEO Analysis Engine
After crawling, each validated page is passed through 11 independent analysis modules (see [SEO Modules](#seo-modules)). Each module returns an issues list, a score contribution, and suggested actions. Results are aggregated into a weighted overall SEO score (0–100).

### Plugin System
A second execution mode for approval-gated workflows. Submit proposed URL/content changes via `POST /plugin/run`, approve with `POST /plugin/approve`, and receive a before/after SEO score comparison. Useful for CMS pipelines and agency review workflows.

### Sitemap Generation
After a successful crawl, a spec-compliant `sitemap.xml` is generated from the validated URL set. Priority is assigned by path depth (homepage = 1.0, top-level = 0.8, deeper = 0.6/0.4). Supports `.xml.gz` compression for Search Console submission.

### Results Dashboard
A Jinja2-rendered tabbed UI at `/results?task_id=...` shows the SEO score, per-module issue lists, keyword gap analysis, and prioritized suggested actions. Supports both standard and plugin result modes.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home / input form |
| `GET` | `/results?task_id=` | Results dashboard |
| `POST` | `/crawl/start` | Start a crawl & audit task |
| `GET` | `/crawl/result/{task_id}` | Fetch completed crawl result |
| `GET` | `/tasks/{task_id}/status` | Poll task state |
| `POST` | `/plugin/run` | Submit a plugin run |
| `POST` | `/plugin/approve` | Approve a pending plugin run |
| `GET` | `/plugin/status/{task_id}` | Poll plugin task state |
| `GET` | `/metrics` | Prometheus metrics |

**Task states:** `pending` → `running` → `complete` |

---

## Security

- **Security headers** — every response includes `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`, and `HSTS`
- **Rate limiting** — per-IP throttling via slowapi; violations return HTTP 429
- **CORS** — configurable via `ALLOWED_ORIGINS` env variable
- **Path safety** — `is_safe_path()` screens all user-supplied paths for traversal attacks
- **Audit logging** — security-relevant events written to `audit.log`
- **Enterprise mode** — when `APP_ENV=enterprise`, Swagger/ReDoc are disabled and errors return generic messages

---

## Getting Started

### Local Development

```bash
git clone https://github.com/Almogod/UrlForger.git
cd UrlForger

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

uvicorn app:app --reload --port 8000
```

Visit `http://localhost:8000`.

### Docker

```bash
docker build -t urlforger:latest .

docker run -p 8000:8000 \
  -e APP_ENV=production \
  -e REDIS_URL=redis://redis:6379/0 \
  -e ALLOWED_ORIGINS=https://yourdomain.com \
  urlforger:latest
```

The Dockerfile uses a multi-stage build: Stage 1 installs dependencies; Stage 2 is a lean runtime image with Playwright's Chromium and all required system libraries pre-installed, running uvicorn with 4 workers.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `production` or `enterprise` for hardened mode |
| `SENTRY_DSN` | _(none)_ | Sentry DSN — leave unset to disable |
| `ALLOWED_ORIGINS` | `*` | Comma-separated allowed CORS origins |
| `REDIS_URL` | _(none)_ | Redis URL for multi-worker task state |
| `MAX_CRAWL_DEPTH` | `3` | Max link depth to follow |
| `MAX_PAGES` | `200` | Max pages per crawl task |
| `RATE_LIMIT` | `10/minute` | slowapi rate limit string |

---

## SEO Modules

| Module | What It Checks |
|---|---|
| `meta` | `<title>` and `<meta description>` — presence, length, uniqueness |
| `heading_structure` | Single `<h1>`, logical H1→H2→H3 cascade, keyword in H1 |
| `image_seo` | `alt` attribute presence and quality on all `<img>` tags |
| `core_web_vitals` | Estimated LCP, FID, CLS from page weight and render-blocking signals |
| `page_speed` | Script/stylesheet count, total page weight, unminified resources |
| `open_graph` | `og:title`, `og:description`, `og:image`, `og:url` completeness |
| `content_quality` | Word count, thin content, keyword density, duplicate paragraphs |
| `mobile_seo` | Viewport meta tag, touch-target size, font legibility |
| `page_experience` | HTTPS enforcement, intrusive interstitial detection |
| `structured_data_validator` | JSON-LD / Microdata presence, required fields per schema type |
| `hreflang` | Language tag correctness and return-link verification |
| `broken_links` | Internal link probing — 404s, redirect loops, broken `#anchor` targets |
| `keyword_gap` | Site-wide keyword extraction and cross-page coverage mapping |

---

## Use Cases

**Auditing an AI-generated site** — Submit a URL, wait for the crawl to complete, review the tabbed results dashboard for your SEO score and per-module issues, download the generated `sitemap.xml`, fix issues, re-audit.

**CMS / agency plugin workflow** — Submit proposed new pages via `POST /plugin/run`, approve via `POST /plugin/approve`, receive a before/after score comparison before any content goes live.

**Automated sitemap refresh** — Call `POST /crawl/start` from a cron job after each site deployment to always have a fresh, validated sitemap ready for Search Console.

**Broken link monitoring** — Use the `broken_links` module output to catch internal 404s introduced by CMS slug changes or page deletions.

---
