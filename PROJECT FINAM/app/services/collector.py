from typing import List, Dict, Any
from app.models.schemas import TimeWindow
from app.services.platform_client import PlatformClient
import logging

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
                return news_data

        except Exception as e:
            logger.error(f"❌ Ошибка при сборе новостей: {e}")
            return []

    async def test_connection(self) -> bool:
        try:
            async with self.platform_client as client:
                test_window = TimeWindow(hours=1)
                news = await client.get_news(test_window)
                return len(news) >= 0
        except Exception as e:
            logger.error(f"❌ Тест подключения не пройден: {e}")
            return False
