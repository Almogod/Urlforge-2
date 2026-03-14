# src/content/engine.py
"""
The Content Generation Engine orchestrates the discovery of keyword gaps
between the user's site and competitors, and generates optimized content
to fill those gaps.
"""

from src.content.competitor_analyzer import analyze_competitors
from src.content.page_generator import generate_page
from src.utils.logger import logger

def run_content_engine(site_pages, competitor_urls, llm_config, limit=3):
    """
    1. Identify keywords from site_pages.
    2. Identify keywords from competitor_urls.
    3. Find gaps.
    4. For top gaps, generate content briefs and then full pages.
    """
    logger.info("Content Generation Engine started")
    
    # In a real scenario, we'd reuse the logic from keyword_gap module
    # For now, let's assume we have the gaps or we extract them here.
    
    # For the sake of this implementation, we'll focus on the 'Actionable' part:
    # Taking a list of keywords and generating pages.
    pass

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
