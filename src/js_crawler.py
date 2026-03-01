import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def crawl_js(start_url, limit=50):
    """Asynchronous crawler that handles JavaScript-rendered content."""
    visited = set()
    to_visit = {start_url}
    results = []

    async with async_playwright() as p:
        # Launching browser; headless=True is standard for crawlers
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while to_visit and len(visited) < limit:
            url = to_visit.pop()

            if url in visited:
                continue

            try:
                # wait_until="domcontentloaded" is faster for simple scraping
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                html = await page.content()
                visited.add(url)

                results.append({
                    "url": url,
                    "status": 200,
                    "html": html
                })

                # Parsing with BeautifulSoup and lxml for speed
                soup = BeautifulSoup(html, "lxml")
                for link in soup.find_all("a", href=True):
                    new_url = urljoin(url, link["href"])
                    
                    # Ensure we stay on the same domain
                    if urlparse(new_url).netloc == urlparse(start_url).netloc:
                        if new_url not in visited:
                            to_visit.add(new_url)
            except Exception:
                # Silently skip failed pages to keep the crawler running
                continue

        await browser.close()
    return results

def crawl_js_sync(start_url, limit=50):
    """Synchronous wrapper compatible with existing event loops (e.g., Jupyter)."""
    try:
        # Check if an event loop is already running in this thread
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Create a new loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Run the async crawler until completion
        return loop.run_until_complete(crawl_js(start_url, limit))
    finally:
        # Avoid closing a loop that might be shared by other processes
        if not loop.is_running():
            try:
                loop.close()
            except Exception:
                pass
