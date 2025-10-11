import whisper
import logging
from pathlib import Path
from typing import Dict
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)

# Load model một lần duy nhất (tránh load lại nhiều lần)
_whisper_model = None

def get_whisper_model(model_size: str = "base"):
    """Lazy load Whisper model"""
    global _whisper_model
    if _whisper_model is None:
        logger.info(f"🔄 Loading Whisper model: {model_size}")
        _whisper_model = whisper.load_model(model_size)
        logger.info("✅ Whisper model loaded")
    return _whisper_model


def extract_audio(video_path: str, audio_path: str) -> str:
    """
    Trích xuất audio từ video
    
    Args:
        video_path: Đường dẫn file video
        audio_path: Đường dẫn lưu audio
        
    Returns:
        Đường dẫn file audio
    """
    try:
        logger.info(f"🎵 Extracting audio from: {video_path}")
        
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        logger.info(f"✅ Audio extracted to: {audio_path}")
        return audio_path
        
    except Exception as e:
        logger.error(f"❌ Audio extraction error: {e}")
        raise


def transcribe_audio(audio_path: str, language: str = None) -> Dict:
    """
    Chuyển audio thành text bằng Whisper
    
    Args:
        audio_path: Đường dẫn file audio
        language: Ngôn ngữ (None = auto detect)
        
    Returns:
        dict chứa full_transcript và segments với timestamps
    """
    try:
        logger.info(f"🎤 Transcribing audio: {audio_path}")
        
        # Load model
        model = get_whisper_model("base")  # Có thể thay bằng "small", "medium", "large"
        
        # Transcribe
        result = model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            verbose=False
        )
        
        full_text = result['text'].strip()
        segments = result['segments']
        
        logger.info(f"✅ Transcription completed: {len(full_text)} characters, {len(segments)} segments")
        
        return {
            'full_transcript': full_text,
            'segments': segments,
            'language': result.get('language', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise


def transcribe_video(video_path: str, audio_output_dir: str) -> Dict:
    """
    Workflow đầy đủ: Extract audio + Transcribe
    
    Args:
        video_path: Đường dẫn file video
        audio_output_dir: Thư mục lưu audio
        
    Returns:
        dict chứa transcript data
    """
    try:
        # Tạo đường dẫn audio
        video_name = Path(video_path).stem
        audio_path = Path(audio_output_dir) / f"{video_name}.mp3"
        
        # Extract audio
        extract_audio(str(video_path), str(audio_path))
        
        # Transcribe
        result = transcribe_audio(str(audio_path))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Video transcription error: {e}")
        raise