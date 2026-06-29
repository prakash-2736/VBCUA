import os
import librosa
import numpy as np
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import config

logger = config.logger

def get_audio_duration(file_path_or_data):
    """Get the duration of an audio file in seconds."""
    try:
        if isinstance(file_path_or_data, tuple):
            y, sr = file_path_or_data
        else:
            y, sr = librosa.load(file_path_or_data, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        return float(duration)
    except Exception as e:
        logger.error(f"Error getting duration: {e}")
        return 0.0

def extract_audio_features(file_path_or_data):
    """
    Extracts key audio metrics from an audio file:
    - Duration
    - RMS Energy (Loudness)
    - Pause Ratio
    - Speech Duration
    - Number of Pauses
    - Speech Confidence (based on spectral flatness and energy)
    """
    try:
        if isinstance(file_path_or_data, tuple):
            y, sr = file_path_or_data
        else:
            y, sr = librosa.load(file_path_or_data, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr)
        
        if duration == 0:
            return {
                "duration": 0.0,
                "rms_energy": 0.0,
                "pause_ratio": 0.0,
                "speech_duration": 0.0,
                "num_pauses": 0,
                "speech_confidence": 0.0
            }
        
        rms_frames = librosa.feature.rms(y=y)
        mean_rms = float(np.mean(rms_frames))
        
       
        non_silent_intervals = librosa.effects.split(y, top_db=35)
        
        if len(non_silent_intervals) > 0:
            non_silent_samples = sum(end - start for start, end in non_silent_intervals)
            speech_duration = float(non_silent_samples / sr)
            speech_duration = min(speech_duration, duration)
            silence_duration = duration - speech_duration
            pause_ratio = float(silence_duration / duration)
            num_pauses = max(0, len(non_silent_intervals) - 1)
        else:
            speech_duration = 0.0
            pause_ratio = 1.0
            num_pauses = 0
            
       
        flatness = librosa.feature.spectral_flatness(y=y)
        rms_threshold = np.percentile(rms_frames, 20)
        active_frames = rms_frames[0] > rms_threshold
        
        if np.any(active_frames):
            mean_flatness = np.mean(flatness[0][active_frames])
        else:
            mean_flatness = np.mean(flatness)
            
        speech_confidence = float(np.clip(1.0 - mean_flatness, 0.0, 1.0))
        
        if mean_rms < 0.005:
            speech_confidence *= (mean_rms / 0.005)
            
        return {
            "duration": float(duration),
            "rms_energy": float(mean_rms),
            "pause_ratio": float(np.clip(pause_ratio, 0.0, 1.0)),
            "speech_duration": float(speech_duration),
            "num_pauses": int(num_pauses),
            "speech_confidence": float(np.clip(speech_confidence, 0.0, 1.0))
        }
        
    except Exception as e:
        logger.error(f"Error extracting audio features: {e}")
        return {
            "duration": 0.0,
            "rms_energy": 0.0,
            "pause_ratio": 0.0,
            "speech_duration": 0.0,
            "num_pauses": 0,
            "speech_confidence": 0.0
        }

def generate_waveform_plot(file_path_or_data, output_filename="waveform.png"):
    """
    Generates a high-quality visualization of the waveform.
    Uses an elegant dark theme with a vibrant blue/cyan waveform
    and highlights the non-silent vs silent segments.
    """
    fig = None
    try:
        if isinstance(file_path_or_data, tuple):
            y, sr = file_path_or_data
        else:
            y, sr = librosa.load(file_path_or_data, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr)
        time = np.linspace(0, duration, len(y))
        
        plt.style.use('dark_background')
        # Optimized memory usage by setting DPI to 100 (reduces raw canvas RAM consumption)
        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=100)
        
        if len(y) > 50000:
            step = len(y) // 50000
            y_plot = y[::step]
            time_plot = time[::step]
        else:
            y_plot = y
            time_plot = time
            
        ax.plot(time_plot, y_plot, color='#00F2FE', alpha=0.8, linewidth=1.5, label='User Speech')
        
        ax.fill_between(time_plot, y_plot, color='#4FACFE', alpha=0.2)
        
        non_silent_intervals = librosa.effects.split(y, top_db=35)
        for i, interval in enumerate(non_silent_intervals):
            start_time = interval[0] / sr
            end_time = interval[1] / sr
            if i == 0:
                ax.axvspan(start_time, end_time, color='#00FF87', alpha=0.08, label='Detected Speech')
            else:
                ax.axvspan(start_time, end_time, color='#00FF87', alpha=0.08)
                
        ax.set_title("Speech Waveform and Activity Analysis", fontsize=14, pad=15, color='#FFFFFF', weight='bold')
        ax.set_xlabel("Time (seconds)", fontsize=11, color='#A0AEC0', labelpad=8)
        ax.set_ylabel("Amplitude", fontsize=11, color='#A0AEC0', labelpad=8)
        ax.grid(True, linestyle='--', color='#2D3748', alpha=0.5)
        ax.set_xlim(0, duration)
        
        ax.legend(loc='upper right', frameon=True, facecolor='#1A202C', edgecolor='#2D3748', fontsize=9)
        
        for spine in ax.spines.values():
            spine.set_color('#2D3748')
            spine.set_linewidth(1.2)
            
        plt.tight_layout()
        
        output_path = os.path.join(config.TEMP_DIR, output_filename)
        plt.savefig(output_path, facecolor='#121212', edgecolor='none', bbox_inches='tight')
        return output_path
    except Exception as e:
        logger.error(f"Error generating waveform plot: {e}")
        return None
    finally:
        if fig is not None:
            fig.clf()
            plt.close(fig)
        plt.close('all')
        import gc
        gc.collect()
