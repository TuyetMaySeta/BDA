import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Khởi tạo OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def summarize_text(text: str, max_length: int = 500) -> str:
    """
    Tạo summary từ full transcript bằng OpenAI GPT
    
    Args:
        text: Full transcript cần tóm tắt
        max_length: Độ dài tối đa của summary (từ)
        
    Returns:
        Summary text
    """
    try:
        if not text or not text.strip():
            logger.warning("⚠️ Empty text for summarization")
            return "Không có nội dung để tóm tắt."
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-...":
            logger.warning("⚠️ OpenAI API key not configured, returning truncated text")
            return text[:500] + "..." if len(text) > 500 else text
        
        logger.info("🤖 Generating summary with OpenAI...")
        
        prompt = f"""Hãy tóm tắt nội dung video sau đây bằng tiếng Việt một cách ngắn gọn và súc tích (khoảng {max_length} từ):

Nội dung:
{text[:4000]}  # Giới hạn để không vượt quá token limit

Yêu cầu:
- Tóm tắt các ý chính
- Ngắn gọn, dễ hiểu
- Bằng tiếng Việt
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # hoặc "gpt-4" nếu có budget
            messages=[
                {"role": "system", "content": "Bạn là trợ lý AI chuyên tóm tắt nội dung video."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        
        summary = response.choices[0].message.content.strip()
        logger.info(f"✅ Summary generated: {len(summary)} characters")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Summarization error: {e}")
        # Fallback: trả về đoạn đầu của text
        return text[:500] + "..." if len(text) > 500 else text


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """
    Trích xuất keywords từ text bằng OpenAI
    
    Args:
        text: Text cần trích xuất keywords
        max_keywords: Số lượng keywords tối đa
        
    Returns:
        List keywords
    """
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-...":
            return []
        
        logger.info("🤖 Extracting keywords with OpenAI...")
        
        prompt = f"""Trích xuất {max_keywords} từ khóa quan trọng nhất từ nội dung sau, trả về dạng danh sách phân cách bằng dấu phẩy:

{text[:2000]}

Chỉ trả về các từ khóa, không giải thích."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia trích xuất từ khóa."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5,
        )
        
        keywords_text = response.choices[0].message.content.strip()
        keywords = [k.strip() for k in keywords_text.split(',')]
        
        logger.info(f"✅ Extracted {len(keywords)} keywords")
        return keywords[:max_keywords]
        
    except Exception as e:
        logger.error(f"❌ Keyword extraction error: {e}")
        return []