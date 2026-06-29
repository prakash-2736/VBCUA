import re

FILLER_WORDS = [
    r"\bum\b",
    r"\buh\b",
    r"\blike\b",
    r"\bactually\b",
    r"\bbasically\b",
    r"\bsort\s+of\b",
    r"\bkind\s+of\b"
]

def analyze_filler_words(text):
    """
    Detects filler words in the transcript, counts them, and calculates the ratio.
    Returns:
        dict: A dictionary with:
            - 'count': total number of filler words.
            - 'ratio': filler words per 100 words.
            - 'detections': dict mapping each filler pattern to its count.
            - 'feedback': recommendations regarding filler words.
    """
    if not text.strip():
        return {
            "count": 0,
            "ratio": 0.0,
            "detections": {},
            "feedback": "No speech detected to analyze."
        }
        
    text_lower = text.lower()
    
    clean_text = re.sub(r'[^\w\s]', '', text_lower)
    words = clean_text.split()
    total_words = len(words)
    
    detections = {}
    total_fillers = 0
    
    for pattern in FILLER_WORDS:
        label = pattern.replace(r"\b", "").replace(r"\s+", " ")
        
        matches = re.findall(pattern, text_lower)
        count = len(matches)
        if count > 0:
            detections[label] = count
            total_fillers += count
            
    ratio = (total_fillers / total_words) * 100 if total_words > 0 else 0.0
    
    if ratio == 0:
        feedback = "Excellent! No filler words were detected in your explanation."
    elif ratio <= 2.0:
        feedback = "Great job! Very minimal filler word usage. Your speech is clean and direct."
    elif ratio <= 5.0:
        feedback = "Moderate usage of filler words. Try to replace filler words with brief, silent pauses to organize your thoughts."
    else:
        feedback = "High usage of filler words. Slow down your speaking pace and plan your sentences to reduce reliance on words like 'like', 'actually', or 'um'."
        
    return {
        "count": total_fillers,
        "ratio": round(ratio, 2),
        "detections": detections,
        "feedback": feedback
    }

def calculate_understanding_score(semantic_score, audio_features, filler_ratio):
    """
    Combines semantic similarity, speech confidence, pause ratio, speaking rate, 
    and filler ratio into a unified evaluation score (0 - 100).
    
    Weights:
    - Semantic Similarity: 50%
    - Speech Confidence: 15%
    - Filler Word Penalty: 15%
    - Pause Ratio: 10%
    - Speaking Rate (WPM): 10%
    """
    duration = audio_features.get("duration", 0.0)
    speech_confidence = audio_features.get("speech_confidence", 0.0)
    pause_ratio = audio_features.get("pause_ratio", 0.0)
    
    if duration == 0:
        return {
            "overall_score": 0.0,
            "semantic_score": 0.0,
            "audio_score": 0.0,
            "speech_rate_score": 0.0,
            "pause_score": 0.0,
            "filler_score": 0.0,
            "filler_ratio": round(float(filler_ratio), 2),
            "classification": "Poor Understanding",
            "suggestions": ["Please record a valid audio response."]
        }
        
    wpm = audio_features.get("wpm", 130.0)
    if 110 <= wpm <= 150:
        speech_rate_score = 100.0
    elif wpm < 110:
        speech_rate_score = max(0.0, (wpm / 110.0) * 100.0)
    else: # wpm > 150
        speech_rate_score = max(0.0, 100.0 - (wpm - 150.0) * 2.0)
        
    if 0.10 <= pause_ratio <= 0.25:
        pause_score = 100.0
    elif pause_ratio < 0.10:
        pause_score = (pause_ratio / 0.10) * 100.0
    else: # pause_ratio > 0.25
        pause_score = max(0.0, 100.0 - ((pause_ratio - 0.25) / 0.25) * 100.0)
        
    filler_score = max(0.0, 100.0 - (filler_ratio * 15.0))
    
    confidence_score = speech_confidence * 100.0
    
    audio_score = (confidence_score * 0.35) + (filler_score * 0.35) + (pause_score * 0.15) + (speech_rate_score * 0.15)
    
    overall_score = (semantic_score * 0.50) + (audio_score * 0.50)
    overall_score = round(overall_score, 2)
    
    if overall_score >= 80.0:
        classification = "Strong Understanding"
    elif overall_score >= 50.0:
        classification = "Moderate Understanding"
    else:
        classification = "Poor Understanding"
        
    suggestions = []
    
    if semantic_score >= 85.0:
        suggestions.append("Your explanation is semantically highly accurate and aligns closely with the reference concept.")
    elif semantic_score >= 60.0:
        suggestions.append("You covered the core ideas, but could expand on technical details, definitions, or mechanisms.")
    else:
        suggestions.append("Consider reviewing the primary definitions and key principles of this topic. The explanation lacks several critical semantic nodes.")
        
    if wpm < 100:
        suggestions.append(f"Your speaking rate ({int(wpm)} WPM) is a bit slow. Try to speak more fluently to keep the explanation engaging.")
    elif wpm > 160:
        suggestions.append(f"Your speaking rate ({int(wpm)} WPM) is too rapid. Slow down to improve articulation and help the evaluator follow along.")
        
    if pause_ratio > 0.30:
        suggestions.append("You had long or frequent silences. Practice structuring your thoughts beforehand to maintain a smoother flow.")
    elif pause_ratio < 0.08:
        suggestions.append("You spoke almost without pausing. Incorporate natural pauses at sentence boundaries to make your speech sound more composed.")
        
    if filler_ratio > 4.0:
        suggestions.append("Reduce your usage of filler phrases. Practice breathing or pausing briefly instead of voicing 'uh', 'um', or 'like'.")
        
    if confidence_score < 60.0:
        suggestions.append("Your speech signal showed vocal instability or low volume. Speak closer to the microphone and project your voice clearly.")

    return {
        "overall_score": float(max(0.0, min(100.0, overall_score))),
        "semantic_score": round(semantic_score, 2),
        "audio_score": round(audio_score, 2),
        "speech_rate_score": round(speech_rate_score, 2),
        "pause_score": round(pause_score, 2),
        "filler_score": round(filler_score, 2),
        "filler_ratio": round(float(filler_ratio), 2),
        "classification": classification,
        "suggestions": suggestions
    }
