def execute_fixes(context, module_results, strategy):

    actions = []

    for module_name in strategy:

        result = module_results.get(module_name)

        if not result:
            continue

        if module_name == "meta":
            actions += apply_meta_fixes(result)

        elif module_name == "schema":
            actions += apply_schema_fixes(result)

        elif module_name == "image_seo":
            actions += apply_image_fixes(result)

    return actions


def apply_meta_fixes(result):

    fixes = result.get("fixes", {})
    actions = []

    for url, data in fixes.items():

        actions.append({
            "type": "update_meta",
            "url": url,
            "title": data.get("title"),
            "description": data.get("description")
        })

    return actions


def apply_schema_fixes(result):

    schemas = result.get("schemas", {})
    actions = []

    for url, schema in schemas.items():

        actions.append({
            "type": "inject_schema",
            "url": url,
            "schema": schema
        })

    return actions


def apply_image_fixes(result):

    fixes = result.get("fixes", {})
    actions = []

    for url, page_fixes in fixes.items():

        for fix in page_fixes:

            actions.append({
                "type": "image_fix",
                "url": url,
                "fix": fix
            })

    return actions
