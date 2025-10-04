import time
import logging
from typing import List
from app.models.schemas import TimeWindow, RadarResponse, NewsEvent
from app.services.collector import NewsCollector
from app.services.processor import NewsProcessor
from app.services.ranker import NewsRanker
from app.services.generator import DraftGenerator
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RadarPipeline:
    def __init__(self):
        self.collector = NewsCollector()
        self.processor = NewsProcessor()
        self.ranker = NewsRanker()
        self.generator = DraftGenerator()

    async def process_time_window(self, time_window: TimeWindow) -> RadarResponse:
        start_time = time.time()

        try:
            logger.info("📡 Собираем новости...")
            raw_news = await self.collector.collect_news(time_window)
            logger.info(f"📊 Собрано {len(raw_news)} новостей")

            logger.info("🔧 Обрабатываем и дедуплицируем...")
            news_clusters = self.processor.process_news(raw_news)
            logger.info(f"📦 Получено {len(news_clusters)} кластеров")

            logger.info("🎯 Ранжируем по горячести...")
            ranked_clusters = self.ranker.rank_clusters(news_clusters)

            top_clusters = ranked_clusters[:settings.TOP_K_EVENTS]

            logger.info("✍️ Генерируем черновики...")
            news_events: List[NewsEvent] = []

            for cluster in top_clusters:
                if cluster['hotness'] >= settings.HOTNESS_THRESHOLD:
                    event = await self.generator.generate_event(cluster)
                    news_events.append(event)

            processing_time = time.time() - start_time

            return RadarResponse(
                time_window=time_window,
                top_events=news_events,
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"❌ Ошибка в пайплайне: {e}")
            raise
