import os
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional, List

class Settings(BaseSettings):
    # App Settings
    APP_ENV: str = Field(default="enterprise", env="APP_ENV") # development, production, enterprise
    APP_NAME: str = "UrlForge | Autonomous SEO Engine"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Timeouts & Retries (Profile specific)
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    CONCURRENCY: int = 5
    
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT") # json or text
    
    # Auth Settings
    # Mandatory change for enterprise
    SECRET_KEY: SecretStr = Field(default="super-secret-key-change-it", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Infrastructure
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    DATABASE_URL: str = Field(default="sqlite:///./database.db", env="DATABASE_URL")
    
    # Automation / Global Deployment Settings
    AUTOMATION_PLATFORM: str = "filesystem" # filesystem, github, ftp, webhook
    GITHUB_TOKEN: Optional[SecretStr] = Field(default=None, env="GITHUB_TOKEN")
    GITHUB_REPO: str = Field(default="user/repo", env="GITHUB_REPO")
    GITHUB_BRANCH: str = Field(default="main", env="GITHUB_BRANCH")
    
    FTP_HOST: str = Field(default="", env="FTP_HOST")
    FTP_USER: str = Field(default="", env="FTP_USER")
    FTP_PASSWORD: Optional[SecretStr] = Field(default=None, env="FTP_PASSWORD")
    
    # LLM Settings
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[SecretStr] = Field(default=None, env="GEMINI_API_KEY")
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    
    CRAWL_TIMEOUT: int = 30
    CRAWLER_PROXY: Optional[str] = Field(default=None, env="CRAWLER_PROXY")
    CRAWLER_BASIC_AUTH: Optional[str] = Field(default=None, env="CRAWLER_BASIC_AUTH") # user:pass
    CRAWLER_BEARER_TOKEN: Optional[str] = Field(default=None, env="CRAWLER_BEARER_TOKEN")
    
    # Storage Settings
    # Path for traditional JSON (deprecated soon)
    TASK_STORE_PATH: str = "tasks.json"
    AUDIT_LOG_PATH: str = "audit.log"

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignore extra env vars


def get_settings() -> Settings:
    settings = Settings()
    
    # Apply Enterprise Defaults
    if settings.APP_ENV == "enterprise":
        settings.TIMEOUT = 10
        settings.MAX_RETRIES = 1
        settings.CONCURRENCY = 50
    elif settings.APP_ENV == "production":
        settings.TIMEOUT = 15
        settings.MAX_RETRIES = 2
        settings.CONCURRENCY = 20

    return settings

config = get_settings()
