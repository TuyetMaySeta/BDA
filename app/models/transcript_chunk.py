from dataclasses import dataclass
from datetime import datetime
from typing import Optional,List

@dataclass
class TranscriptChunk:
    """Model cho bảng transcript_chunks"""
    id: Optional[int] = None
    video_id: int = 0
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    start_time: float = 0.0
    end_time: float = 0.0
    text: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'chunk_index': self.chunk_index,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }