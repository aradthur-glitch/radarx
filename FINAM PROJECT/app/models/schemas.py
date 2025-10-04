from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class TimeWindow(BaseModel):
    hours: int = 24
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Source(BaseModel):
    url: HttpUrl
    source_name: str
    published_at: datetime
    type: str

class Timeline(BaseModel):
    first_mention: datetime
    confirmation: Optional[datetime] = None
    last_update: datetime

class NewsEvent(BaseModel):
    headline: str
    hotness: float
    why_now: str
    entities: List[str]
    sources: List[Source]
    timeline: Timeline
    draft: Dict[str, Any]
    dedup_group: str

class RadarResponse(BaseModel):
    time_window: TimeWindow
    top_events: List[NewsEvent]
    processing_time: float
