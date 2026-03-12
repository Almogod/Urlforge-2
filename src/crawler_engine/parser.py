from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def extract_links(html, base_url):

    soup = BeautifulSoup(html, "lxml")

    links = []

    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"])

        if urlparse(url).scheme.startswith("http"):
            links.append(url)

    return links
