import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.pipeline import RadarPipeline
from app.models.schemas import TimeWindow
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    pipeline = RadarPipeline()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: pipeline.process_time_window(TimeWindow(hours=24)),
        'interval',
        hours=1
    )
    scheduler.start()
    logger.info("🕐 Scheduler запущен: анализ каждый час")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
