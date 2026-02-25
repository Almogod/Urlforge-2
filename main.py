from src.crawler import crawl
from src.extractor import extract_metadata
from src.normalizer import normalize
from src.filter import is_valid
from src.generator import generate_sitemap

def build_clean_urls(pages):
    clean = set()

    for p in pages:
        meta = extract_metadata(p)

        if is_valid(meta):
            url = normalize(meta["url"])
            clean.add(url)

    return list(clean)

if __name__ == "__main__":
    domain = input("Enter domain (e.g., https://example.com): ").strip()

    print("Crawling...")
    pages = crawl(domain)

    print("Processing...")
    clean_urls = build_clean_urls(pages)

    print("Generating sitemap...")
    generate_sitemap(clean_urls)

    print(f"Done. Generated sitemap.xml with {len(clean_urls)} URLs")
