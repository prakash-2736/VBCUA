# Voice-Based Concept Understanding Analyser (VBCUA)

VBCUA is an AI-powered educational assessment system designed to evaluate how effectively a learner explains conceptual topics using speech. The system combines Speech-to-Text transcription, Sentence-BERT semantic models, and audio signal processing to score understanding and delivery.

---

## Key Features

- **Speech Transcription**: Integrates OpenAI Whisper locally to transcribe student voice explanations.
- **Semantic Understanding**: Uses a local Sentence-BERT (`all-MiniLM-L6-v2`) transformer to measure the cosine similarity between the student explanation and the target reference concept.
- **Acoustic Feature Extraction**: Utilizes `librosa` and `soundfile` to extract speaking rate (WPM), speech confidence (voicing stability), and pauses (ratio & count).
- **Filler Word Detection**: Locates common speech filler terms (e.g. *um*, *uh*, *like*, *actually*, *basically*) and reports counts and ratios.
- **Intelligent Scoring & Classification**: Merges all metrics to score student understanding (0-100) and classifies performance (*Strong*, *Moderate*, or *Poor*).
- **Visual Waveform Analysis**: Plots audio amplitude and visually highlights silent regions.
- **PDF Report Generation**: Assembles evaluation scores, detailed benchmarks, waveform plots, and AI-driven tips into a professional ReportLab PDF document suitable for portfolio platforms (e.g. SkillWallet).

---

## Project Structure

```text
VBCUA/
├── app.py               # Streamlit interactive dashboard entrypoint
├── speech_to_text.py     # OpenAI Whisper transcription wrapper
├── semantic_eval.py      # Sentence-BERT similarity computation
├── audio_utils.py        # Audio signal processing, feature extraction, and waveform plotting
├── scoring_engine.py     # Aggregated scoring models & filler word checkers
├── report_generator.py   # ReportLab PDF compilation
├── config.py             # Preset challenge concepts & path rules
├── requirements.txt      # Dependency specification
├── assets/               # Static assets & logos
├── reports/              # Location for generated PDF reports
└── temp/                 # Space for temporary uploaded/rendered audio and files
```

---

## Installation & Setup

1. **Verify Python Version**:
   This project runs best on Python 3.11.x to ensure full compatibility with ML libraries (`torch`, `numba`).
   
2. **Create and Activate Virtual Environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## How to Run

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

Open the local address printed by Streamlit (default: `http://localhost:8501`) in your web browser.

### Demo Mode
If you do not have a microphone or a pre-recorded WAV file, click the **"Run Demo Evaluation"** button in the dashboard. The application will generate a synthetic WAV tone and evaluate a pre-configured sample explanation to show the full semantic and acoustic analysis dashboard.
