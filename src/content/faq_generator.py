# src/content/faq_generator.py
"""
Robust AI FAQ Generator for sitewide SERP optimization.
Extracts core topics and user-intent patterns to generate high-value,
structured Q&A based on Google's E-E-A-T and helpful content guidelines.
"""

import re
import json
from collections import Counter
from src.utils.logger import logger
from src.content.stopwords import STOPWORDS
from src.content.content_schema import FAQItem

def generate_site_faqs(pages, domain, llm_config) -> list[FAQItem]:
    """
    Generate a robust list of 6-8 FAQItems based on the site's content.
    Ensures high-quality, citation-worthy Q&A.
    """
    logger.info(f"Generating robust site FAQs for {domain}")
    
    # 1. Extract core topics and common user-intent queries
    topics = []
    for p in pages:
        titles = f"{p.get('title', '')} {' '.join(p.get('headings', []))}"
        words = re.sub(r"[^a-zA-Z0-9\s]", " ", titles).lower().split()
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
        topics.extend(filtered)
    
    if not topics:
        topics = ["services", "solutions", "technology", "support"]
        
    top_topics = [t for t, count in Counter(topics).most_common(12)]
    
    faqs = []
    has_api = bool(llm_config.get("api_key")) or llm_config.get("provider") == "ollama"

    if has_api:
        faqs = _generate_faqs_with_llm(top_topics, domain, llm_config)
    
    if not faqs:
        faqs = _generate_faqs_builtin(top_topics, domain)

    # 4. Final step: Normalize all to FAQItem model for strict schema adherence
    robust_faqs = []
    for item in faqs:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            # Basic validation
            if len(item["question"]) > 10 and len(item["answer"]) > 20:
                robust_faqs.append(FAQItem(question=item["question"], answer=item["answer"]))
    
    return robust_faqs

def _generate_faqs_with_llm(topics, domain, llm_config):
    """Call LLM with an engineered prompt for high-quality citation FAQs."""
    from src.content.page_generator import _call_openai, _call_gemini, _call_ollama
    
    prompt = f"""
    You are an expert SEO content strategist for '{domain}'.
    Based on these core topics found on the site: {', '.join(topics)}, 
    generate 7 high-impact, citation-worthy FAQ questions and answers.
    
    STRATEGY:
    - Target "Featured Snippets" and "People Also Ask" (PAA) intent.
    - Focus on authoritative, factual answers (E-E-A-T).
    - Use "Who, What, How, Why, Is" patterns.
    - Keep answers concise but comprehensive (40-60 words).
    
    Strictly format your response as a valid JSON array of objects with "question" and "answer" fields ONLY.
    """
    
    provider = llm_config.get("provider", "openai").lower()
    raw = None
    try:
        if provider == "openai":
            raw = _call_openai(prompt, llm_config)
        elif provider == "gemini":
            raw = _call_gemini(prompt, llm_config)
        elif provider == "ollama":
            raw = _call_ollama(prompt, llm_config)
            
        if raw:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
    except Exception as e:
        logger.warning(f"Robust FAQ LLM generation failed for {domain}: {e}")
    return []

def _generate_faqs_builtin(topics, domain):
    """High-quality fallback engine with pattern-aware template generation."""
    faqs = []
    # Mix topics to create believable, non-generic questions
    templates = [
        ("What core services does {domain} provide regarding {topic}?", 
         "At {domain}, we specialize in delivering high-volume {topic} solutions tailored for enterprise scalability and individual precision. Our approach focuses on reliability and modern performance standards."),
        
        ("How does {domain} implement {topic} for maximum efficiency?", 
         "We utilize advanced {topic} frameworks that integrate seamlessly with your existing stack. By prioritizing optimized workflows, {domain} ensures that every implementation meets your strategic goals."),
        
        ("Why is {topic} considered a critical component of {domain}'s strategy?", 
         "{topic} is central to our mission of providing state-of-the-art results. It allows us to maintain a competitive edge and ensure that our clients receive the most up-to-date innovations in the field."),
        
        ("Are the {topic} solutions at {domain} secure and compliant?", 
         "Security is our top priority. Every {topic} integration follows strict industry-standard protocols and encryption, ensuring that your data and operations are always protected under the latest compliance guidelines."),
        
        ("Can {domain} customize {topic} features for specific niches?", 
         "Absolutely. We pride ourselves on the flexibility of our {topic} offerings. Our engineering team works closely with you to adapt these features to the unique requirements of your industry or specific use case."),
        
        ("What sets {domain}'s approach to {topic} apart from competitors?", 
         "Our edge lies in the combination of deep domain expertise in {topic} and an obsessive focus on user experience. Unlike generic alternatives, {domain} builds for long-term sustainability and performance.")
    ]
    
    for i, (q_tpl, a_tpl) in enumerate(templates):
        topic = topics[i % len(topics)].capitalize()
        # Ensure we don't repeat the same topic for consecutive questions
        faqs.append({
            "question": q_tpl.format(topic=topic, domain=domain),
            "answer": a_tpl.format(topic=topic, domain=domain)
        })
    return faqs
