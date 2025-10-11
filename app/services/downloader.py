import yt_dlp
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def download_video(url: str, output_dir: Path) -> dict:
    """
    Download video từ YouTube
    
    Returns:
        dict chứa thông tin video và đường dẫn file
    """
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            return {
                'video_id': info['id'],
                'title': info['title'],
                'channel': info['uploader'],
                'duration': info['duration'],
                'published_at': info.get('upload_date'),
                'file_path': output_dir / f"{info['id']}.mp4"
            }
            
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        raise