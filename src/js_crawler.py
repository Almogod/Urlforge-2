import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def crawl_js(start_url, limit=200):
    visited = set()
    to_visit = set([start_url])
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while to_visit and len(visited) < limit:
            url = to_visit.pop()

            if url in visited:
                continue

            # --- UPDATED NAVIGATION LOGIC START ---
            try:
                # Using domcontentloaded is significantly faster than networkidle
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                html = await page.content()
            except Exception:
                # If the page fails to load, skip to the next URL in to_visit
                continue
            # --- UPDATED NAVIGATION LOGIC END ---

            visited.add(url)

            results.append({
                "url": url,
                "status": 200,
                "html": html
            })

            soup = BeautifulSoup(html, "lxml")

            for link in soup.find_all("a", href=True):
                new_url = urljoin(url, link["href"])

                # Ensure we only crawl URLs within the same domain
                if urlparse(new_url).netloc == urlparse(start_url).netloc:
                    if new_url not in visited:
                        to_visit.add(new_url)

        await browser.close()

    return results


def crawl_js_sync(start_url, limit=200):
    """
    Synchronous wrapper to run the async crawler using [asyncio.run](https://docs.python.org).
    """
    return asyncio.run(crawl_js(start_url, limit))
