from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging

from app.config import settings
from services.database import init_db, get_db
from services.downloader import download_video
from services.transcriber import transcribe_audio
from services.chunker import chunk_transcript
from services.summarizer import summarize_text

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI app
app = FastAPI(
    title="YouTube Video Processor",
    description="Xử lý video YouTube: download, transcribe, summarize",
    version="1.0.0"
)

# Pydantic models
class VideoRequest(BaseModel):
    url: HttpUrl

class VideoResponse(BaseModel):
    id: int
    title: str
    url: str
    status: str
    message: str

# Event startup
@app.on_event("startup")
async def startup_event():
    """Khởi tạo database khi start app"""
    init_db()
    logger.info("✅ Application started successfully")

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YouTube Video Processor API",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/api/videos", response_model=VideoResponse)
async def process_video(video_request: VideoRequest):
    """
    Xử lý video YouTube
    
    Steps:
    1. Download video
    2. Extract metadata
    3. Transcribe audio
    4. Chunk transcript
    5. Summarize
    6. Save to database
    """
    try:
        url = str(video_request.url)
        logger.info(f"📥 Processing video: {url}")
        
        # TODO: Implement full processing pipeline
        # Hiện tại chỉ return mock response
        
        return VideoResponse(
            id=1,
            title="Video đang được xử lý",
            url=url,
            status="processing",
            message="Video đã được thêm vào hàng đợi xử lý"
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{video_id}")
async def get_video(video_id: int):
    """Lấy thông tin video theo ID"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, url, channel_name, duration, 
                   published_at, summary, created_at
            FROM videos 
            WHERE id = %s
        """, (video_id,))
        
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "id": result[0],
            "title": result[1],
            "url": result[2],
            "channel_name": result[3],
            "duration": result[4],
            "published_at": result[5],
            "summary": result[6],
            "created_at": result[7]
        }
        
    finally:
        cursor.close()

@app.get("/api/videos/{video_id}/chunks")
async def get_video_chunks(video_id: int):
    """Lấy tất cả chunks của video"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT id, chunk_index, start_time, end_time, text
            FROM transcript_chunks 
            WHERE video_id = %s
            ORDER BY chunk_index
        """, (video_id,))
        
        results = cursor.fetchall()
        
        return {
            "video_id": video_id,
            "total_chunks": len(results),
            "chunks": [
                {
                    "id": row[0],
                    "chunk_index": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "text": row[4]
                }
                for row in results
            ]
        }
        
    finally:
        cursor.close()