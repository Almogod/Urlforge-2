import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl(start_url, limit=200):
    visited = set()
    to_visit = [(start_url, 0)]  # (url, depth)
    results = []

    domain = urlparse(start_url).netloc
    depth_limit = 2

    with httpx.Client(timeout=10, follow_redirects=True) as client:
        while to_visit and len(visited) < limit:
            url, depth = to_visit.pop(0)

            if url in visited or depth > depth_limit:
                continue

            try:
                r = client.get(url)
                visited.add(url)

                results.append({
                    "url": url,
                    "status": r.status_code,
                    "html": r.text
                })

                if "text/html" not in r.headers.get("content-type", ""):
                    continue

                soup = BeautifulSoup(r.text, "lxml")

                # 1. Extract normal links
                for link in soup.find_all("a", href=True):
                    new_url = urljoin(url, link["href"])

                    if urlparse(new_url).netloc == domain:
                        to_visit.append((new_url, depth + 1))

                # 2. Extract canonical
                canonical = soup.find("link", rel="canonical")
                if canonical and canonical.get("href"):
                    new_url = urljoin(url, canonical["href"])
                    if urlparse(new_url).netloc == domain:
                        to_visit.append((new_url, depth + 1))

            except:
                continue

    return results
