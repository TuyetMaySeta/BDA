import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

def get_openai_client():
    """Lazy load OpenAI client"""
    from openai import OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_embedding(text: str) -> List[float]:
    """
    Tạo embedding vector từ text bằng OpenAI
    
    Args:
        text: Text cần embedding
        
    Returns:
        List[float]: Vector embedding (1536 dimensions)
    """
    try:
        if not text or not text.strip():
            logger.warning("⚠️ Empty text for embedding")
            return None
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-...":
            logger.warning("⚠️ OpenAI API key not configured")
            return None
        
        logger.info("🔢 Generating embedding...")
        
        client = get_openai_client()
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Giới hạn độ dài
        )
        
        embedding = response.data[0].embedding
        logger.info(f"✅ Embedding generated: {len(embedding)} dimensions")
        
        return embedding
        
    except Exception as e:
        logger.error(f"❌ Embedding error: {e}")
        return None


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Tạo embeddings cho nhiều texts cùng lúc
    
    Args:
        texts: List các text cần embedding
        
    Returns:
        List[List[float]]: List các embedding vectors
    """
    try:
        if not texts:
            return []
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-...":
            logger.warning("⚠️ OpenAI API key not configured")
            return [None] * len(texts)
        
        logger.info(f"🔢 Generating {len(texts)} embeddings...")
        
        client = get_openai_client()
        
        # Truncate texts
        texts = [t[:8000] if t else "" for t in texts]
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        embeddings = [item.embedding for item in response.data]
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"❌ Batch embedding error: {e}")
        return [None] * len(texts)