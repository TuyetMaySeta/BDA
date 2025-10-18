from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.services.database import (
    init_db, get_db, insert_video, insert_chunks, 
    update_video_summary, check_video_exists
)
from app.services.downloader import download_video
from app.services.transcriber import transcribe_video
from app.services.chunker import chunk_transcript
from app.services.summarizer import summarize_text

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    try:
        #init_db()
        logger.info("✅ Application started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YouTube Video Processor API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "process_video": "POST /api/videos",
            "get_video": "GET /api/videos/{video_id}",
            "get_chunks": "GET /api/videos/{video_id}/chunks"
        }
    }


def process_video_pipeline(url: str) -> dict:
    """
    Pipeline xử lý video đầy đủ
    
    Steps:
    1. Check video đã tồn tại chưa
    2. Download video
    3. Extract metadata & transcribe
    4. Chunk transcript
    5. Generate summary
    6. Save to database
    """
    try:
        logger.info(f"{'='*60}")
        logger.info(f"🚀 Starting pipeline for: {url}")
        logger.info(f"{'='*60}")
        
        # Step 1: Check existing
        existing_id = check_video_exists(url)
        if existing_id:
            logger.info(f"⚠️ Video already exists with ID: {existing_id}")
            return {
                'video_id': existing_id,
                'status': 'already_exists',
                'message': 'Video đã tồn tại trong database'
            }
        
        # Step 2: Download video
        logger.info("📥 Step 1: Downloading video...")
        video_info = download_video(url, Path(settings.VIDEO_DIR))
        logger.info(f"✅ Downloaded: {video_info['title']}")
        
        # Step 3: Transcribe
        logger.info("🎤 Step 2: Transcribing audio...")
        transcript_data = transcribe_video(
            str(video_info['file_path']),
            settings.AUDIO_DIR
        )
        logger.info(f"✅ Transcribed: {len(transcript_data['full_transcript'])} characters")
        
        # Step 4: Chunk transcript
        logger.info("✂️ Step 3: Chunking transcript...")
        chunks = chunk_transcript(
            transcript_data['segments'],
            chunk_duration=settings.CHUNK_SIZE
        )
        logger.info(f"✅ Created {len(chunks)} chunks")
        
        # Step 5: Generate summary
        logger.info("📝 Step 4: Generating summary...")
        summary = summarize_text(transcript_data['full_transcript'])
        logger.info(f"✅ Summary generated: {len(summary)} characters")
        
        # Step 6: Save to database
        logger.info("💾 Step 5: Saving to database...")
        
        # Convert published_at from YYYYMMDD to datetime
        published_at = None
        if video_info.get('published_at'):
            try:
                date_str = video_info['published_at']
                published_at = datetime.strptime(date_str, '%Y%m%d')
            except:
                pass
        
        # Insert video
        video_data = {
            'title': video_info['title'],
            'url': url,
            'channel_name': video_info['channel'],
            'full_transcript': transcript_data['full_transcript'],
            'duration': video_info['duration'],
            'published_at': published_at,
            'summary': summary
        }
        
        video_id = insert_video(video_data)
        
        # Insert chunks
        insert_chunks(video_id, chunks)
        
        logger.info(f"{'='*60}")
        logger.info(f"✅ Pipeline completed successfully! Video ID: {video_id}")
        logger.info(f"{'='*60}")
        
        return {
            'video_id': video_id,
            'title': video_info['title'],
            'status': 'completed',
            'message': 'Video đã được xử lý thành công',
            'stats': {
                'duration': video_info['duration'],
                'transcript_length': len(transcript_data['full_transcript']),
                'chunks_count': len(chunks),
                'summary_length': len(summary)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}", exc_info=True)
        raise


@app.post("/api/videos", response_model=VideoResponse)
async def process_video(video_request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Xử lý video YouTube (async với background tasks)
    """
    try:
        url = str(video_request.url)
        logger.info(f"📥 Received request for: {url}")
        
        # Xử lý ngay (synchronous) - cho project nhỏ
        # Nếu muốn async, dùng: background_tasks.add_task(process_video_pipeline, url)
        
        result = process_video_pipeline(url)
        
        return VideoResponse(
            id=result['video_id'],
            title=result.get('title', 'Unknown'),
            url=url,
            status=result['status'],
            message=result['message']
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
            SELECT id, title, url, channel_name, full_transcript, duration, 
                   published_at, summary, created_at, updated_at
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
            "full_transcript": result[4],
            "duration": result[5],
            "published_at": result[6],
            "summary": result[7],
            "created_at": result[8],
            "updated_at": result[9]
        }
        
    finally:
        cursor.close()
        db.close()


@app.get("/api/videos/{video_id}/chunks")
async def get_video_chunks(video_id: int):
    """Lấy tất cả chunks của video"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT id, chunk_index, start_time, end_time, text, created_at
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
                    "text": row[4],
                    "created_at": row[5]
                }
                for row in results
            ]
        }
        
    finally:
        cursor.close()
        db.close()


@app.get("/api/videos")
async def list_videos(limit: int = 10, offset: int = 0):
    """Lấy danh sách videos"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, url, channel_name, duration, summary, created_at
            FROM videos 
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        results = cursor.fetchall()
        
        return {
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "videos": [
                {
                    "id": row[0],
                    "title": row[1],
                    "url": row[2],
                    "channel_name": row[3],
                    "duration": row[4],
                    "summary": row[5],
                    "created_at": row[6]
                }
                for row in results
            ]
        }
        
    finally:
        cursor.close()
        db.close()