from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Video:
    """Model cho bảng videos"""
    id: Optional[int] = None
    title: str = ""
    url: str = ""
    channel_name: Optional[str] = None
    full_transcript: Optional[str] = None
    duration: Optional[int] = None
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'channel_name': self.channel_name,
            'full_transcript': self.full_transcript,
            'duration': self.duration,
            'published_at': self.published_at,
            'summary': self.summary,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }