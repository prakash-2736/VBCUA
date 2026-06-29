import os
import whisper
import streamlit as st
import config

logger = config.logger


@st.cache_resource(max_entries=1)
def get_whisper_model(model_size="base"):
    """
    Lazy loads and caches Whisper models by size using Streamlit's cache_resource.
    Supported sizes: 'tiny', 'base', 'small', 'medium', 'large'
    """
    logger.info(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)
    logger.info("Whisper model loaded successfully.")
    return model


def transcribe_audio(file_path_or_array, model_size="base"):
    """
    Transcribes the speech in an audio file or NumPy array using Whisper.
    Returns:
        dict: A dictionary containing:
            - 'text': The full transcribed text (str).
            - 'segments': Detailed segment transcripts with timestamps (list).
            - 'error': Error message if transcription failed, else None.
    """
    if isinstance(file_path_or_array, str):
        if not os.path.exists(file_path_or_array):
            return {
                "text": "",
                "segments": [],
                "error": f"Audio file not found: {file_path_or_array}",
            }

    try:
        model = get_whisper_model(model_size)
        result = model.transcribe(file_path_or_array, fp16=False)
        return {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", []),
            "error": None,
        }
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}")
        return {
            "text": "",
            "segments": [],
            "error": str(e),
        }
