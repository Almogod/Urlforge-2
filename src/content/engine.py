# src/content/engine.py
"""
The Content Generation Engine orchestrates the discovery of keyword gaps
between the user's site and competitors, and generates optimized content
to fill those gaps.
"""

from src.content.competitor_analyzer import analyze_competitors
from src.content.page_generator import generate_page
from src.services.competitor_discovery import discover_competitors
from src.utils.logger import logger
import re
from collections import Counter

def run_content_engine(site_pages, competitor_urls, llm_config, limit=3, domain=None):
    """
    1. Identify keywords from site_pages.
    2. Auto-discover competitors if none provided.
    3. Identify keywords from competitor_urls.
    4. Find gaps (Keywords competitors have, site lacks).
    5. Recommend top gaps for page generation.
    """
    logger.info("Content Generation Engine started")
    
    if not competitor_urls and domain:
        competitor_urls = discover_competitors(domain, llm_config)
    
    # Simple keyword extraction from titles/meta
    site_keywords = _extract_bulk_keywords(site_pages)
    
    # Gap analysis
    gaps = {}
    for comp_url in competitor_urls[:3]:
        # In a real app, we'd fetch the competitor home/blog here
        # For simplicity, we simulate finding unique keywords from them
        comp_keywords = ["seo strategy", "content marketing", "digital growth", "backlink building", "conversion optimization"]
        gap_kws = [kw for kw in comp_keywords if kw not in site_keywords]
        if gap_kws:
            gaps[comp_url] = gap_kws[:3]
            
    return {
        "keyword_gap": gaps,
        "site_keywords": list(site_keywords)[:20],
        "recommendations": [{"keyword": kw, "source": url} for url, kws in gaps.items() for kw in kws]
    }

def _extract_bulk_keywords(pages):
    tokens = []
    for p in pages:
        text = f"{p.get('url', '')} {p.get('title', '')} {p.get('meta_description', '')}"
        tokens.extend(re.findall(r'\w{5,}', text.lower()))
    
    # Remove common SEO stop words if any...
    return set(tokens)

def generate_content_for_keyword(keyword, competitor_urls, llm_config, existing_pages=None):
    """
    Targeted generation for a single keyword.
    """
    try:
        logger.info(f"Generating content for keyword: {keyword}")
        
        # 1. Build Brief
        brief = analyze_competitors(competitor_urls, keyword, "")
        
        # 2. Generate Page
        result = generate_page(brief, llm_config, existing_pages)
        
        return result
    except Exception as e:
        logger.error(f"Failed to generate content for {keyword}: {str(e)}")
        return {"error": str(e)}
