from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import TimeWindow, RadarResponse
from app.services.pipeline import RadarPipeline
from app.api.endpoints import router as api_router

app = FastAPI(
    title="RADAR API",
    description="Система поиска и оценки горячих новостей в финансах",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

pipeline = RadarPipeline()

@app.get("/")
async def root():
    return {"message": "RADAR API работает 🚀", "platform": "Интеграция с вашей платформой"}

@app.post("/analyze", response_model=RadarResponse)
async def analyze_news(time_window: TimeWindow):
    try:
        result = await pipeline.process_time_window(time_window)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RADAR"}