import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

def get_db():
    """Tạo kết nối database"""
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        raise

def init_db():
    """Khởi tạo database schema"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Tìm file schema.sql
        schema_path = Path(__file__).parent.parent.parent / "database" / "schema.sql"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("✅ Database schema initialized")
        else:
            logger.warning(f"⚠️ schema.sql not found at {schema_path}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def insert_video(video_data: Dict) -> int:
    """
    Insert video vào database
    
    Returns:
        video_id
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO videos (title, url, channel_name, full_transcript, duration, published_at, summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            video_data.get('title'),
            video_data.get('url'),
            video_data.get('channel_name'),
            video_data.get('full_transcript'),
            video_data.get('duration'),
            video_data.get('published_at'),
            video_data.get('summary')
        ))
        
        video_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.info(f"✅ Inserted video with id: {video_id}")
        return video_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error inserting video: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def insert_chunks(video_id: int, chunks: List[Dict]):
    """Insert transcript chunks vào database"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO transcript_chunks (video_id, chunk_index, start_time, end_time, text)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                video_id,
                chunk.get('chunk_index'),
                chunk.get('start_time'),
                chunk.get('end_time'),
                chunk.get('text')
            ))
        
        conn.commit()
        logger.info(f"✅ Inserted {len(chunks)} chunks for video {video_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error inserting chunks: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def update_video_summary(video_id: int, summary: str):
    """Update summary cho video"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE videos 
            SET summary = %s, updated_at = NOW()
            WHERE id = %s
        """, (summary, video_id))
        
        conn.commit()
        logger.info(f"✅ Updated summary for video {video_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error updating summary: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def check_video_exists(url: str) -> Optional[int]:
    """Kiểm tra video đã tồn tại chưa, trả về video_id nếu có"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM videos WHERE url = %s", (url,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()