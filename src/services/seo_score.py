def compute_score(engine_results):
    """
    Weighted SEO Score computation based on module importance.
    Critical: Meta, Broken Links, Mobile SEO
    Major: Headings, CWV, Schema
    Minor: OG, Hreflang, Page Speed
    """
    
    weights = {
        "meta": 15,
        "broken_links": 20,
        "mobile_seo": 10,
        "heading_structure": 10,
        "core_web_vitals": 10,
        "structured_data_validator": 10,
        "image_seo": 5,
        "open_graph": 5,
        "page_speed": 5,
        "hreflang": 5,
        "content_quality": 5
    }
    
    total_score = 100
    deduction = 0
    
    modules = engine_results.get("modules", {})
    for module_name, weight in weights.items():
        result = modules.get(module_name)
        if not result:
            continue
            
        issues = result.get("issues", [])
        if not issues:
            continue
            
        # Deduct proportional to issue count, capped at the module weight
        # 1 issue = 50% of module weight, 2+ issues = 100% of weight
        issue_count = len(issues)
        if issue_count == 1:
            deduction += weight * 0.5
        elif issue_count > 1:
            deduction += weight

    final_score = int(total_score - deduction)
    
    # Mix with audit baseline (40/60 split)
    audit_baseline = engine_results.get("audit", {}).get("score", 100)
    weighted_final = int((final_score * 0.7) + (audit_baseline * 0.3))
    
    return max(0, min(100, weighted_final))
