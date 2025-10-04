from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.collector import NewsCollector
from app.models.schemas import TimeWindow

router = APIRouter()
collector = NewsCollector()

@router.post("/test-connection")
async def test_platform_connection():
    try:
        is_connected = await collector.test_connection()
        return {
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sample-news")
async def get_sample_news(time_window: TimeWindow):
    try:
        news = await collector.collect_news(time_window)
        return {
            "count": len(news),
            "news": news[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TickerRequest(BaseModel):
    ticker: str
    time_window: Optional[TimeWindow] = None

@router.get("/events/{ticker}")
async def get_events_by_ticker(ticker: str, time_window: Optional[TimeWindow] = None):
    if time_window is None:
        time_window = TimeWindow(hours=24)
    try:
        news = await collector.collect_news(time_window)
        filtered = [n for n in news if ticker.upper() in str(n.get('entities', []))]
        return {"count": len(filtered), "events": filtered[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
