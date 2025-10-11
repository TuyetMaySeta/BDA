import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
        # Database
        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/youtube_processor")
        # OpenAi
        OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

        # Paths
        DATA_DIR: str = os.getenv("DATA_DIR", "./data")
        VIDEO_DIR: str = os.getenv("VIDEO_DIR", "./data/videos")
        AUDIO_DIR: str = os.getenv("AUDIO_DIR", "./data/audio")
        TEMP_DIR: str = os.getenv("TEMP_DIR", "./data/temp")
        
        # Settings
        DEBUG: bool = os.getenv("DEBUG", "True") == "True"
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        MAX_VIDEO_DURATION: int = int(os.getenv("MAX_VIDEO_DURATION", "3600"))
        CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "30"))
        
        class Config:
            env_file = ".env"

settings = Settings()


