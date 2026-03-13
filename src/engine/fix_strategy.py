def build_fix_strategy(engine_results):

    strategy = []

    modules = engine_results.get("modules", {})

    for module_name, result in modules.items():

        if not result:
            continue

        if module_name == "meta" and result.get("issues"):
            strategy.append(module_name)

        if module_name == "schema":
            strategy.append(module_name)

        if module_name == "image_seo":
            strategy.append(module_name)

    return strategy
