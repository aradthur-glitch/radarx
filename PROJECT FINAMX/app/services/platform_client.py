import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.schemas import TimeWindow
from aiohttp_retry import RetryClient
import logging
import re

logger = logging.getLogger(__name__)

class PlatformClient:
    def __init__(self):
        self.api_key = settings.PLATFORM_API_KEY
        self.base_url = settings.PLATFORM_API_URL
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        client_session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
        self.session = RetryClient(client_session=client_session, retries=3)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_news(self, time_window: TimeWindow) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            params = {
                "start_time": time_window.start_time.isoformat() if time_window.start_time else
                (datetime.utcnow() - timedelta(hours=time_window.hours)).isoformat(),
                "end_time": time_window.end_time.isoformat() if time_window.end_time else
                datetime.utcnow().isoformat(),
                "limit": settings.MAX_NEWS_PER_SOURCE,
                "language": "en,ru"
            }

            params = {k: v for k, v in params.items() if v is not None}

            async with self.session.get(
                    f"{self.base_url}/news",
                    params=params
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    return self._normalize_news_data(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")

        except asyncio.TimeoutError:
            raise Exception("Platform API timeout")
        except Exception as e:
            raise Exception(f"Failed to fetch news: {str(e)}")

    def _normalize_news_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        normalized_news = []

        news_items = raw_data.get("articles", []) or raw_data.get("news", []) or raw_data.get("items", [])

        for item in news_items:
            normalized = {
                "id": item.get("id") or item.get("url") or str(hash(item.get("title", ""))),
                "title": item.get("title", ""),
                "content": item.get("content") or item.get("description") or item.get("text", ""),
                "summary": item.get("summary", ""),
                "published_at": self._parse_datetime(
                    item.get("published_at") or item.get("date") or item.get("timestamp")),
                "url": item.get("url") or item.get("link", ""),
                "source": item.get("source") or item.get("publisher", "unknown"),
                "author": item.get("author", ""),
                "language": item.get("language", "en"),
                "entities": item.get("entities", []),
                "sentiment": item.get("sentiment"),
                "category": item.get("category") or item.get("section", "")
            }

            text = normalized.get('title', '') + ' ' + normalized.get('content', '')
            tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
            if 'entities' in normalized:
                normalized['entities'].extend(tickers)
            else:
                normalized['entities'] = list(set(tickers))

            normalized = {k: v for k, v in normalized.items() if v is not None}
            normalized_news.append(normalized)

        return normalized_news

    def _parse_datetime(self, dt_str: Any) -> datetime:
        if isinstance(dt_str, datetime):
            return dt_str

        if not dt_str:
            return datetime.utcnow()

        try:
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            return datetime.utcnow()
        except:
            return datetime.utcnow()
