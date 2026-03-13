def run(context):
    # Placeholder (real fix later via HTML rewriting / CMS)
    urls = context.get("urls", [])

    # For now, just ensure uniqueness
    return {"urls": list(set(urls))}
