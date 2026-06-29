import os
import whisper

_whisper_models = {}


def get_whisper_model(model_size="base"):
    """
    Lazy loads and caches Whisper models by size.
    Supported sizes: 'tiny', 'base', 'small', 'medium', 'large'
    """
    if model_size not in _whisper_models:
        print(f"Loading Whisper model '{model_size}'...")
        _whisper_models[model_size] = whisper.load_model(model_size)
        print("Whisper model loaded successfully.")
    return _whisper_models[model_size]


def transcribe_audio(file_path, model_size="base"):
    """
    Transcribes the speech in an audio file using Whisper.
    Returns:
        dict: A dictionary containing:
            - 'text': The full transcribed text (str).
            - 'segments': Detailed segment transcripts with timestamps (list).
            - 'error': Error message if transcription failed, else None.
    """
    if not os.path.exists(file_path):
        return {
            "text": "",
            "segments": [],
            "error": f"Audio file not found: {file_path}",
        }

    try:
        model = get_whisper_model(model_size)
        result = model.transcribe(file_path, fp16=False)
        return {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", []),
            "error": None,
        }
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return {
            "text": "",
            "segments": [],
            "error": str(e),
        }
