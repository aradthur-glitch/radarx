import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()

class Settings(BaseSettings):
    PLATFORM_API_KEY: str
    PLATFORM_API_URL: str

    MAX_NEWS_PER_SOURCE: int = 100
    HOTNESS_THRESHOLD: float = 0.3
    TOP_K_EVENTS: int = 10

    SENTENCE_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    LLM_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
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