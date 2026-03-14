from src.automation.executors.github_executor import apply_github_actions
from src.utils.logger import logger


def run_automation(actions, config):
    """
    Applies SEO fixes using the configured integration.
    """

    platform = config.get("platform")

    if not actions:
        return {"status": "no_actions"}

    logger.info("Starting automation for platform: %s", platform)

    if platform == "github":
        return apply_github_actions(actions, config)
    elif platform in ["vercel", "hostinger", "ftp", "webhook"]:
        logger.info(f"Deployment to {platform} is accepted. (Implementation pending for specific provider APIs).")
        return {"status": "accepted_for_deployment", "platform": platform}

    return {
        "status": "unsupported_platform",
        "platform": platform
    }
