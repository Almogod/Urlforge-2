from collections import defaultdict
from urllib.parse import urlparse


def generate_audit_report(pages, clean_urls):
    report = {
        "total_pages_crawled": len(pages),
        "total_clean_urls": len(clean_urls),
        "issues": defaultdict(list)
    }

    seen = set()

    for p in pages:
        url = p.get("url")
        status = p.get("status", 0)

        if not url:
            continue

        # Duplicate URLs
        if url in seen:
            report["issues"]["duplicates"].append(url)
        else:
            seen.add(url)

        # Non-200 pages
        if status != 200:
            report["issues"]["non_200"].append(url)

        # Query parameters
        if "?" in url:
            report["issues"]["has_query_params"].append(url)

        # Non-HTTPS
        if url.startswith("http://"):
            report["issues"]["not_https"].append(url)

        # Deep paths (basic heuristic)
        path_depth = len(urlparse(url).path.strip("/").split("/"))
        if path_depth > 4:
            report["issues"]["deep_pages"].append(url)

    # Missing from clean sitemap
    clean_set = set(clean_urls)
    for p in pages:
        url = p.get("url")
        if url and url not in clean_set:
            report["issues"]["excluded_from_sitemap"].append(url)

    return report
