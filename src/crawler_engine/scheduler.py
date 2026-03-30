import asyncio
import httpx
import time
import base64
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from .fetcher import fetch
from src.config import config
from src.utils.logger import logger


async def run_workers(frontier, parser, graph, limit=200, concurrency=10, delay=1.0, check_robots=True, extra_headers=None, broken_links_only=False):
    results = []
    broken_links = []
    rp = None
    
    # 1. Asynchronous robots.txt handling
    if check_robots:
        try:
            # We try to get the base domain from the first available URL
            first_url = None
            if hasattr(frontier, 'peek'):
                first_url = frontier.peek()
            
            if not first_url and hasattr(frontier, 'visited') and frontier.visited:
                first_url = next(iter(frontier.visited))

            if first_url:
                parsed = urlparse(first_url)
                robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(robots_url)
                    if resp.status_code == 200:
                        rp = RobotFileParser()
                        rp.parse(resp.text.splitlines())
                        logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")

    # 2. Client configuration (Proxy & Auth)
    mounts = {}
    if config.CRAWLER_PROXY:
        mounts = {"all://": httpx.AsyncHTTPTransport(proxy=config.CRAWLER_PROXY)}

    headers = {}
    if config.CRAWLER_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {config.CRAWLER_BEARER_TOKEN}"
    elif config.CRAWLER_BASIC_AUTH:
        encoded = base64.b64encode(config.CRAWLER_BASIC_AUTH.encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    
    if extra_headers:
        headers.update(extra_headers)

    async with httpx.AsyncClient(
        timeout=config.CRAWL_TIMEOUT, 
        headers=headers,
        mounts=mounts,
        follow_redirects=True
    ) as client:

        semaphore = asyncio.Semaphore(concurrency)

        async def worker():
            while frontier.size() and len(results) < limit:
                url = frontier.get()
                if not url:
                    break

                # Robots.txt check
                if rp and not rp.can_fetch("*", url):
                    logger.debug(f"Skipping {url} due to robots.txt")
                    continue

                async with semaphore:
                    if delay > 0:
                        await asyncio.sleep(delay)
                    
                    logger.info(f"Worker fetching: {url}")
                    page = await fetch(client, url)

                if not page:
                    logger.warning(f"Worker failed to fetch: {url}")
                    continue

                status = page.get("status")
                # If in broken links mode, we mainly care about Non-200s
                if broken_links_only:
                    if status and status != 200:
                        results.append(page)
                        logger.info(f"Worker found broken link: {url} (Status: {status})")
                else:
                    results.append(page)
                    logger.info(f"Worker fetched {url} (Status: {status}). Progress: {len(results)}/{limit}")

                # Specialist: Even if broken links only, we might want to crawl to find them
                # But if it's 200, and we ARE in broken_links_only, we don't ADD to results, just parse links.
                if status == 200 and page.get("html"):
                    extracted = parser(page["html"], page["url"])
                    
                    page["hreflangs"] = extracted.get("hreflangs", [])
                    page["images"] = extracted.get("images", [])
                    page["videos"] = extracted.get("videos", [])

                    for link in extracted.get("links", []):
                        graph.add_edge(page["url"], link)
                        # The frontier itself now handles domain locking
                        frontier.add(link)

        workers = [worker() for _ in range(concurrency)]
        await asyncio.gather(*workers)

    return results
