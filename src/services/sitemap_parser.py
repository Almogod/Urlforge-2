import httpx
from bs4 import BeautifulSoup

from src.utils.security import is_safe_url


def get_sitemap_urls(domain):
    sitemap_url = domain.rstrip("/") + "/sitemap.xml"
    urls = []

    if not is_safe_url(sitemap_url):
        return []

    try:
        r = httpx.get(sitemap_url, timeout=10)

        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "xml")

        for loc in soup.find_all("loc"):
            urls.append(loc.text.strip())

    except:
        return []

    return urls
