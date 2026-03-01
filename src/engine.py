from src.audit import generate_audit_report
from src.fixer import fix_urls, generate_fix_report


def run_engine(pages, clean_urls):
    # 1. Analyze
    audit = generate_audit_report(pages, clean_urls)

    # 2. Decide fixes
    plan = build_fix_plan(audit)

    # 3. Apply fixes
    fixed_urls = apply_fixes(clean_urls, plan)

    # 4. Summary
    fixes_applied = generate_fix_report(audit)

    return {
        "audit": audit,
        "plan": plan,
        "fixed_urls": fixed_urls,
        "fixes": fixes_applied
    }


# -------------------------
# FIX PLANNER
# -------------------------
def build_fix_plan(audit):
    plan = []

    if audit["issues"]["duplicates"]:
        plan.append("remove_duplicates")

    if audit["issues"]["has_query_params"]:
        plan.append("remove_query_params")

    if audit["issues"]["not_https"]:
        plan.append("force_https")

    if audit["issues"]["non_200"]:
        plan.append("remove_broken")

    return plan


# -------------------------
# FIX EXECUTOR
# -------------------------
def apply_fixes(urls, plan):
    fixed = urls.copy()

    if "remove_query_params" in plan or "force_https" in plan:
        fixed = fix_urls(fixed)

    if "remove_duplicates" in plan:
        fixed = list(set(fixed))

    # Remove broken URLs (basic logic)
    if "remove_broken" in plan:
        fixed = [u for u in fixed if not u.endswith("404")]

    return fixed
