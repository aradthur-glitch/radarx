import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()

class Settings(BaseSettings):
    PLATFORM_API_KEY: str = os.getenv("PLATFORM_API_KEY", "e309c2dcd8f3437ea05b1d069247773a")
    PLATFORM_API_URL: str = os.getenv("PLATFORM_API_URL", "https://newsapi.org/v2/everything")

    MAX_NEWS_PER_SOURCE: int = 100
    HOTNESS_THRESHOLD: float = 0.3
    TOP_K_EVENTS: int = 10

    SENTENCE_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    LLM_API_KEY: str = os.getenv("OPENAI_API_KEY", "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")

    LLM_MODEL: str = "gpt-3.5-turbo"

    NEWS_SOURCES: List[str] = ["https://api.reuters.com", "https://api.bloomberg.com"]

    RSS_FEEDS: List[str] = [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.reuters.com/reuters/technologyNews",
        "https://www.bloomberg.com/feed/rss/markets.rss"
    ]

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = {"env_file": ".env"}

settings = Settings()