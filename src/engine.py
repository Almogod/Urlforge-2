from src.audit import generate_audit_report
from src.engine.registry import MODULE_REGISTRY
from src.engine.planner import build_fix_plan


def run_engine(pages, clean_urls, domain):

    context = {
        "pages": pages,
        "urls": clean_urls,
        "domain": domain,
    }

    # 1. Run audit
    audit = generate_audit_report(pages, clean_urls)

    # 2. Build execution plan
    plan = build_fix_plan(audit)

    results = {
        "audit": audit,
        "plan": plan,
        "modules": {},
        "urls": clean_urls
    }

    # 3. Execute modules
    for module_name in plan:
        module = MODULE_REGISTRY[module_name]

        module_result = module.run(context)

        results["modules"][module_name] = module_result

        # modules may update URLs
        if "urls" in module_result:
            context["urls"] = module_result["urls"]

    results["fixed_urls"] = context["urls"]

    return results
