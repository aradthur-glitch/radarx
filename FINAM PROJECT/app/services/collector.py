from typing import List, Dict, Any
from app.models.schemas import TimeWindow
from app.services.platform_client import PlatformClient
from app.core.config import settings
import feedparser
import logging
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.platform_client = PlatformClient()

    async def collect_news(self, time_window: TimeWindow) -> List[Dict[str, Any]]:
        try:
            async with self.platform_client as client:
                news_data = await client.get_news(time_window)
                logger.info(f"✅ Получено {len(news_data)} новостей из платформы")
                news_data.extend(await self._collect_from_rss(time_window))
                return news_data
        except Exception as e:
            logger.error(f"❌ Ошибка при сборе новостей: {e}")
            return await self._collect_from_rss(time_window)

    @staticmethod
    async def _collect_from_rss(time_window: TimeWindow) -> List[Dict[str, Any]]:
        news_data = []
        start_time = time_window.start_time or (datetime.now(timezone.utc) - timedelta(hours=time_window.hours))
        end_time = time_window.end_time or datetime.now(timezone.utc)
        for rss_url in settings.RSS_FEEDS:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:settings.MAX_NEWS_PER_SOURCE]:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) if 'published_parsed' in entry else datetime.now(timezone.utc)
                    if start_time <= pub_date <= end_time:
                        news_item = {
                            "id": entry.id or str(hash(entry.title)),
                            "title": entry.title,
                            "content": entry.summary or "",
                            "summary": entry.summary or "",
                            "published_at": pub_date,
                            "url": entry.link,
                            "source": feed.feed.title or "RSS",
                            "author": entry.author or "",
                            "language": "en",
                            "entities": [],
                            "sentiment": 0,
                            "category": entry.get('tags', [{}])[0].term if entry.get('tags') else ""
                        }
                        news_data.append(news_item)
                logger.info(f"RSS {rss_url}: {len(feed.entries)} entries")
            except Exception as e:
                logger.error(f"RSS ошибка {rss_url}: {e}")
        return news_data

    async def test_connection(self) -> bool:
        try:
            async with self.platform_client as client:
                test_window = TimeWindow(hours=1)
                news = await client.get_news(test_window)
                return len(news) >= 0
        except Exception as e:
            logger.error(f"❌ Тест подключения не пройден: {e}")
            return False