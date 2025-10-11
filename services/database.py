import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings
import logging
from pathlib import Path

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
        
        # Đọc và chạy schema.sql

        schema_path = Path(settings.DATA_DIR) / "database" / "schema.sql"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("✅ Database schema initialized")
        else:
            logger.warning("⚠️ schema.sql not found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise