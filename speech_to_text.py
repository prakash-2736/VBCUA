import os
import whisper

_whisper_model = None

def get_whisper_model(model_size="base"):
    """
    Lazy loads and caches the Whisper model.
    Supported sizes: 'tiny', 'base', 'small', 'medium', 'large'
    """
    global _whisper_model
    if _whisper_model is None:
        print(f"Loading Whisper model '{model_size}'...")
        _whisper_model = whisper.load_model(model_size)
        print("Whisper model loaded successfully.")
    return _whisper_model

def transcribe_audio(file_path, model_size="base"):
    """
    Transcribes the speech in an audio file using Whisper.
    Returns:
        dict: A dictionary containing:
            - 'text': The full transcribed text (str).
            - 'segments': Detailed segment transcripts with timestamps (list).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    try:
        model = get_whisper_model(model_size)
        
        result = model.transcribe(file_path, fp16=False)
        
        return {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return {
            "text": "",
            "segments": []
        }
