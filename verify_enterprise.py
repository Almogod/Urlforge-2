import asyncio
import httpx
import json
from src.crawler_engine.fetcher import fetch
from src.crawler_engine.parser import extract_links

async def test_enterprise_features():
    print("--- [ENTERPRISE CRAWLER VERIFICATION] ---")
    
    # 1. Test Redirect Chain
    print("\n[Case 1] Redirect Tracking")
    url = "http://google.com"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await fetch(client, url)
        print(f"URL: {url}")
        print(f"Final: {res.get('final_url')}")
        print(f"Hops: {len(res.get('redirect_history', []))}")
        for hop in res.get('redirect_history', []):
            print(f"  -> {hop['status']} {hop['url']}")

    # 2. Test Audit (Title, Dec, H1s, etc.)
    print("\n[Case 2] SEO Audit Data")
    wiki_url = "https://en.wikipedia.org/wiki/Search_engine_optimization"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await fetch(client, wiki_url)
        extracted = extract_links(res["html"], wiki_url, custom_selectors={"main_title": "h1#firstHeading"})
        
        print(f"Title: {res.get('url')}") # Just to see
        print(f"Audit Title: {extracted['meta']['title']}")
        print(f"H1s: {extracted['headings']['h1']}")
        print(f"Custom (Title Selector): {extracted['custom']['main_title']}")

if __name__ == "__main__":
    asyncio.run(test_enterprise_features())
