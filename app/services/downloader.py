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
        # Options để bypass 403
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            
            # Bypass 403 Forbidden
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            
            # Thêm cookies nếu cần
            'cookiefile': None,  # Có thể thêm file cookies nếu cần
            
            # Retry options
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
        }
        
        logger.info(f"📥 Downloading from: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            video_file = output_dir / f"{info['id']}.{info['ext']}"
            
            logger.info(f"✅ Downloaded: {info['title']}")
            
            return {
                'video_id': info['id'],
                'title': info['title'],
                'channel': info.get('uploader', info.get('channel', 'Unknown')),
                'duration': info.get('duration', 0),
                'published_at': info.get('upload_date'),
                'file_path': video_file
            }
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"❌ Download error: {e}")
        
        # Nếu vẫn lỗi 403, thử với format khác
        logger.info("🔄 Retrying with alternative format...")
        
        try:
            ydl_opts_fallback = {
                'format': 'worst',  # Thử format thấp nhất
                'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'video_id': info['id'],
                    'title': info['title'],
                    'channel': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'published_at': info.get('upload_date'),
                    'file_path': output_dir / f"{info['id']}.{info['ext']}"
                }
        except Exception as fallback_error:
            logger.error(f"❌ Fallback also failed: {fallback_error}")
            raise
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise