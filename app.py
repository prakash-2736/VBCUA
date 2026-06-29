import os
import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

import config
import audio_utils
import speech_to_text
import semantic_eval
import scoring_engine
import report_generator

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark Mode Core Aesthetics */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0F172A 0%, #020617 100%);
        color: #F8FAFC;
    }
    
    /* Title and Header Styles */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: left;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
        text-align: left;
    }
    
    /* Card Component */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    /* Pill Styles for Classification */
    .class-pill {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 50px;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .strong-class {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .moderate-class {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .poor-class {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Sidebar styling override */
    [data-testid="stSidebar"] {
        background-color: #0B1329;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

def create_sample_wav():
    """Generates a small valid sample wav file in the temp directory if not present."""
    sample_path = os.path.join(config.TEMP_DIR, "demo_sample.wav")
    if not os.path.exists(sample_path):
        import scipy.io.wavfile as wav
        sample_rate = 16000
        t = np.linspace(0, 4.0, int(sample_rate * 4.0), endpoint=False)
        envelope = np.sin(2 * np.pi * 0.5 * t) ** 2  
        tone1 = np.sin(2 * np.pi * 220 * t)
        tone2 = np.sin(2 * np.pi * 440 * t)
        audio = (0.5 * tone1 + 0.3 * tone2) * envelope
        audio = (audio * 32767).astype(np.int16)
        
        wav.write(sample_path, sample_rate, audio)
    return sample_path

if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None

with st.sidebar:
    st.image("https://img.icons8.com/color/96/microphone.png", width=64)
    st.subheader("Learner Profile Setup")
    student_name = st.text_input("Learner Name", value="", placeholder="Enter name (e.g. John Doe)")
    
    st.markdown("---")
    st.subheader("Conceptual Challenge Selection")
    
    topic_choices = list(config.REFERENCE_CONCEPTS.keys()) + ["Custom Concept..."]
    selected_topic_choice = st.selectbox("Select Topic to Explain:", topic_choices)
    
    if selected_topic_choice == "Custom Concept...":
        custom_topic_name = st.text_input("Custom Concept Title:", "REST APIs")
        reference_text = st.text_area(
            "Reference Concept Explanation:", 
            "Representational State Transfer is an architectural style for network APIs. "
            "It is stateless, client-server based, cacheable, and uses standard HTTP methods "
            "such as GET, POST, PUT, and DELETE to manage resource representations."
        )
        selected_topic = custom_topic_name
    else:
        selected_topic = selected_topic_choice
        reference_text = config.REFERENCE_CONCEPTS[selected_topic]
        st.markdown("**Reference Concept Definition:**")
        st.caption(reference_text)
        
    st.markdown("---")
    st.subheader("Model Parameter Tweaks")
    whisper_model_size = st.selectbox(
        "Whisper Speech-to-Text Model:",
        options=["tiny", "base", "small"],
        index=1,
        help="Higher model sizes offer greater transcription accuracy, but take longer to compute."
    )

st.markdown(f"<div class='main-title'>{config.APP_TITLE}</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Evaluate conceptual understanding and speaking quality with speech-to-text, acoustic features, and semantic modeling.</div>", unsafe_allow_html=True)

col_audio, col_desc = st.columns([2, 1])

with col_audio:
    st.markdown("### 🎙️ Step 1: Input Explanation")
    uploaded_file = st.file_uploader("Upload Audio File (WAV format recommended):", type=["wav", "mp3", "m4a"])
    
with col_desc:
    st.markdown("### 💡 Testing Instructions")
    st.write("1. Choose a concept on the sidebar.")
    st.write("2. Upload an audio recording explaining that concept.")
    st.write("3. Don't have a WAV file? Click the button below to load a simulated audio assessment instantly.")
    
    run_demo = st.button("🚀 Run Demo Evaluation", use_container_width=True)

audio_file_path = None
is_demo = False

if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1]
    audio_file_path = os.path.join(config.TEMP_DIR, f"upload_{int(time.time())}{file_extension}")
    with open(audio_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Audio file uploaded successfully! Ready for analysis.")
elif run_demo:
    audio_file_path = create_sample_wav()
    is_demo = True

if audio_file_path is not None:
    if st.button("🔍 Run Full Concept Evaluation", type="primary", use_container_width=True) or is_demo:
        with st.status("Analyzing explanation... Please wait", expanded=True) as status:
            
            status.write("📂 Loading audio and extracting acoustic parameters...")
            audio_features = audio_utils.extract_audio_features(audio_file_path)
            
            status.write("🗣️ Transcribing speech with OpenAI Whisper (this may take a few seconds)...")
            if is_demo:
                if "OOP" in selected_topic:
                    transcript_text = (
                        "Object oriented programming is a programming paradigm that works with objects and classes. "
                        "It has four main pillars which are encapsulation, inheritance, polymorphism, and abstraction. "
                        "Encapsulation is about binding fields and methods. Inheritance allows creating sub classes. "
                        "Polymorphism allows different classes to share interfaces, and abstraction hides implementation details."
                    )
                elif "TCP" in selected_topic:
                    transcript_text = (
                        "The TCP handshake is the three way handshake to connect a client and server. "
                        "First the client sends a SYN packet to synchronize. Next, the server replies with a SYN ACK "
                        "which stands for synchronize acknowledge. Actually, like, then the client replies back with an ACK packet. "
                        "After this is done, the connection is established and we can transmit data."
                    )
                elif "Photosynthesis" in selected_topic:
                    transcript_text = (
                        "Photosynthesis is how plants make food using sunlight. Basically, it takes carbon dioxide and water "
                        "in the presence of light and chlorophyll to produce glucose and oxygen. It has light dependent reactions "
                        "and the Calvin cycle in the chloroplasts. Uh, sort of, it makes sugars."
                    )
                else:
                    transcript_text = (
                        "Database normalization is the process of organizing data in a database to avoid data redundancy and preserve "
                        "data integrity. We have first normal form which requires atomic values, second normal form which relies on "
                        "full key dependency, and third normal form which makes sure there are no transitive dependencies in the table."
                    )
                
                segments = [{"start": 0.0, "end": 10.0, "text": transcript_text}]
            else:
                transcription_result = speech_to_text.transcribe_audio(audio_file_path, whisper_model_size)
                transcript_text = transcription_result["text"]
                segments = transcription_result["segments"]
                
            status.write("🧠 Performing semantic analysis against reference concept...")
            semantic_results = semantic_eval.calculate_semantic_similarity(transcript_text, reference_text)
            
            status.write("⏱️ Analysing delivery and detecting filler words...")
            filler_results = scoring_engine.analyze_filler_words(transcript_text)
            
            duration = audio_features["duration"]
            if duration > 0:
                words_count = len(transcript_text.split())
                wpm = (words_count / duration) * 60.0
            else:
                wpm = 0.0
            audio_features["wpm"] = wpm
            
            status.write("📈 Integrating scores & evaluating performance...")
            scoring_results = scoring_engine.calculate_understanding_score(
                semantic_results["similarity_score"],
                audio_features,
                filler_results["ratio"]
            )
            
            status.write("📊 Generating visual acoustics graph...")
            waveform_plot_path = audio_utils.generate_waveform_plot(audio_file_path, "current_waveform.png")
            
            status.write("📄 Building professional PDF report...")
            pdf_path = os.path.join(config.REPORTS_DIR, f"evaluation_report_{int(time.time())}.pdf")
            report_generator.generate_pdf_report(
                student_name,
                selected_topic,
                transcript_text,
                reference_text,
                audio_features,
                scoring_results,
                waveform_plot_path,
                pdf_path
            )
            
            st.session_state.evaluation = {
                "transcript": transcript_text,
                "audio_features": audio_features,
                "semantic_results": semantic_results,
                "filler_results": filler_results,
                "scoring_results": scoring_results,
                "waveform_plot_path": waveform_plot_path,
                "pdf_path": pdf_path,
                "topic": selected_topic,
                "reference_concept": reference_text,
                "student_name": student_name
            }
            status.update(label="Evaluation Complete!", state="complete", expanded=False)

eval_data = st.session_state.evaluation

if eval_data is not None:
    st.markdown("---")
    
    tab_overview, tab_semantic, tab_acoustic, tab_pdf = st.tabs([
        "📋 Overview Dashboard", 
        "🧠 Semantic Concept Alignment", 
        "🎙️ Acoustic & Delivery Analysis", 
        "📄 Download & Export PDF"
    ])
    
    scoring_results = eval_data["scoring_results"]
    audio_features = eval_data["audio_features"]
    semantic_results = eval_data["semantic_results"]
    filler_results = eval_data["filler_results"]
    classification = scoring_results["classification"]
    
    class_class = "poor-class"
    if classification == "Strong Understanding":
        class_class = "strong-class"
    elif classification == "Moderate Understanding":
        class_class = "moderate-class"
        
    with tab_overview:
        st.markdown("### Evaluation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Overall Score</div>
                <div class="metric-value" style="color: #4FACFE;">{scoring_results['overall_score']:.1f}%</div>
                <div>Concept & Voice aggregate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Concept Similarity</div>
                <div class="metric-value" style="color: #00F2FE;">{scoring_results['semantic_score']:.1f}%</div>
                <div>Sentence-BERT match</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Speaking Quality</div>
                <div class="metric-value" style="color: #00FF87;">{scoring_results['audio_score']:.1f}%</div>
                <div>Acoustic delivery index</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="height: 100%;">
                <div class="metric-title">Classification</div>
                <div class="class-pill {class_class}">{classification}</div>
                <div style="margin-top: 0.5rem;">SkillWallet Benchmark</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_feedback, col_chart = st.columns([5, 3])
        
        with col_feedback:
            st.markdown("#### 💡 AI Recommendations & Actionable Suggestions")
            for sugg in scoring_results["suggestions"]:
                st.markdown(f"- {sugg}")
                
            st.markdown("#### 🗣️ Transcribed Explanation Speech")
            st.info(f"\"{eval_data['transcript']}\"")
            
        with col_chart:
            st.markdown("#### 📊 Metric Weighting Breakdown")
            
            scores_df = pd.DataFrame({
                "Metric": [
                    "Semantic Similarity", 
                    "Speech Confidence", 
                    "Filler Word Score", 
                    "Pause Score", 
                    "Speech Rate Score"
                ],
                "Score (0-100)": [
                    scoring_results["semantic_score"],
                    audio_features["speech_confidence"] * 100.0,
                    scoring_results["filler_score"],
                    scoring_results["pause_score"],
                    scoring_results["speech_rate_score"]
                ]
            })
            st.bar_chart(data=scores_df, x="Metric", y="Score (0-100)", color="#4FACFE")
            
    with tab_semantic:
        st.markdown("### Concept Mapping and Content Coverage")
        
        col_st, col_ref = st.columns(2)
        
        with col_st:
            st.markdown("**Your Transcribed Explanation**")
            st.caption(f"Word count: {len(eval_data['transcript'].split())} words")
            st.write(eval_data['transcript'])
            
        with col_ref:
            st.markdown("**Target Concept Reference Definition**")
            st.caption(f"Word count: {len(eval_data['reference_concept'].split())} words")
            st.write(eval_data['reference_concept'])
            
        st.markdown("---")
        st.markdown("#### Semantic Scoring Metrics")
        col_cos, col_res = st.columns(2)
        with col_cos:
            st.metric("Raw Embedding Cosine Similarity", f"{semantic_results['raw_cosine']:.4f}")
            st.caption("Cosine similarity measures the angle between semantic vector representations. High similarity reflects conceptual alignment regardless of exact word matching.")
        with col_res:
            st.metric("Scaled Similarity Rating", f"{semantic_results['similarity_score']:.1f}%")
            st.caption("Normalized percentage indicating coverage of the target concepts compared to reference answers.")
            
    with tab_acoustic:
        st.markdown("### Acoustic Delivery & Speaking Features")
        
        col_acoustic_graph, col_acoustic_metrics = st.columns([5, 3])
        
        with col_acoustic_graph:
            if eval_data["waveform_plot_path"] and os.path.exists(eval_data["waveform_plot_path"]):
                st.image(eval_data["waveform_plot_path"], caption="Voice Amplitude & Speech-Silence Segmentation Graph", use_container_width=True)
            else:
                st.warning("Waveform plot not available.")
                
        with col_acoustic_metrics:
            st.markdown("#### Delivery Performance Breakdown")
            
            st.metric("Speaking Pace", f"{int(audio_features['wpm'])} Words / Min", 
                      delta="Optimal: 110-150" if 110 <= audio_features['wpm'] <= 150 else "Sub-optimal")
                      
            st.metric("Pause Ratio", f"{audio_features['pause_ratio']*100:.1f}% of speech",
                      delta="Optimal: 10%-25%" if 0.10 <= audio_features['pause_ratio'] <= 0.25 else "Sub-optimal")
                      
            st.metric("Speech Confidence Index", f"{audio_features['speech_confidence']*100:.1f}%",
                      help="Measures voicing stability and energy above the noise floor.")
                      
            st.metric("Filler Words Used", f"{filler_results['count']} filler(s) ({filler_results['ratio']:.1f}%)")
            st.caption(filler_results["feedback"])
            
            if filler_results["detections"]:
                st.markdown("**Detected Fillers Breakdown:**")
                st.write(pd.DataFrame(list(filler_results["detections"].items()), columns=["Filler word", "Count"]))

    with tab_pdf:
        st.markdown("### Export Evaluation Report")
        st.write("Generate and download a professional academic report in PDF format. This report can be submitted to faculty, portfolio platforms, or included in your SkillWallet dashboard.")
        
        pdf_path = eval_data["pdf_path"]
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                
            st.download_button(
                label="📥 Download PDF Evaluation Report",
                data=pdf_bytes,
                file_name=f"VBCUA_Evaluation_{selected_topic.replace(' ', '_')}_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.success("PDF Report generated successfully and is ready for download.")
            
            st.markdown("#### Report Document Details")
            st.info(f"""
            - **Document Type:** Voice-Based Concept Understanding Evaluation Report
            - **Institution/Context:** SkillWallet Academic Portfolio
            - **Student Name:** {student_name if student_name else 'Anonymous Learner'}
            - **Evaluated Concept:** {selected_topic}
            - **Overall Score:** {scoring_results['overall_score']:.1f}%
            - **Classification:** {classification}
            - **File Path:** `{pdf_path}`
            """)
        else:
            st.error("Generated PDF report not found.")
