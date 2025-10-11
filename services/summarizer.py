# chunker.py
def chunk_transcript(segments: list, chunk_size: int = 30) -> list:
    """Chia transcript thành chunks theo thời gian"""
    chunks = []
    current_chunk = {
        'start_time': 0,
        'end_time': 0,
        'text': ''
    }
    
    for segment in segments:
        # Logic chia chunk ở đây
        pass
    
    return chunks

# summarizer.py
def summarize_text(text: str) -> str:
    """Tạo summary từ full transcript"""
    # Dùng OpenAI/Claude API hoặc model khác
    return "Summary of the video..."