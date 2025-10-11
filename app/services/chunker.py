import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def chunk_transcript(segments: List[Dict], chunk_duration: int = 30) -> List[Dict]:
    """
    Chia transcript thành chunks theo thời gian
    
    Args:
        segments: List các segment từ Whisper (có 'start', 'end', 'text')
        chunk_duration: Thời lượng mỗi chunk (giây)
        
    Returns:
        List các chunks với start_time, end_time, text
    """
    try:
        if not segments:
            logger.warning("⚠️ No segments to chunk")
            return []
        
        chunks = []
        current_chunk = {
            'start_time': 0.0,
            'end_time': 0.0,
            'text': ''
        }
        
        chunk_index = 0
        current_chunk['start_time'] = segments[0]['start']
        
        for segment in segments:
            segment_start = segment['start']
            segment_end = segment['end']
            segment_text = segment['text'].strip()
            
            # Nếu segment này vượt quá chunk_duration, tạo chunk mới
            if segment_end - current_chunk['start_time'] > chunk_duration:
                # Lưu chunk hiện tại
                if current_chunk['text']:
                    current_chunk['end_time'] = segment_start
                    current_chunk['chunk_index'] = chunk_index
                    chunks.append(current_chunk.copy())
                    chunk_index += 1
                
                # Bắt đầu chunk mới
                current_chunk = {
                    'start_time': segment_start,
                    'end_time': segment_end,
                    'text': segment_text,
                    'chunk_index': chunk_index
                }
            else:
                # Thêm vào chunk hiện tại
                current_chunk['text'] += ' ' + segment_text
                current_chunk['end_time'] = segment_end
        
        # Thêm chunk cuối cùng
        if current_chunk['text']:
            current_chunk['chunk_index'] = chunk_index
            chunks.append(current_chunk)
        
        logger.info(f"✅ Created {len(chunks)} chunks from {len(segments)} segments")
        return chunks
        
    except Exception as e:
        logger.error(f"❌ Chunking error: {e}")
        raise