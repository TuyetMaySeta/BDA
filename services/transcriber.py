import whisper
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str) -> dict:
    """
    Chuyển audio thành text bằng Whisper
    
    Returns:
        dict chứa full_transcript và segments với timestamps
    """
    try:
        # Load model (base/small/medium/large)
        model = whisper.load_model("base")
        
        # Transcribe
        result = model.transcribe(audio_path)
        
        return {
            'full_transcript': result['text'],
            'segments': result['segments']  # Có timestamps
        }
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise