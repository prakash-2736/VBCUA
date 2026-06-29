from sentence_transformers import SentenceTransformer, util
import numpy as np

_sbert_model = None

def get_sbert_model(model_name="all-MiniLM-L6-v2"):
    """
    Lazy loads and caches the Sentence-Transformer model.
    'all-MiniLM-L6-v2' is very fast, accurate, and has a small footprint (~80MB).
    """
    global _sbert_model
    if _sbert_model is None:
        print(f"Loading Sentence-BERT model '{model_name}'...")
        _sbert_model = SentenceTransformer(model_name)
        print("Sentence-BERT model loaded successfully.")
    return _sbert_model

def calculate_semantic_similarity(student_text, reference_text):
    """
    Computes the cosine similarity between the student's transcribed explanation
    and the reference concept explanation.
    
    Returns:
        dict: A dictionary containing:
            - 'similarity_score': Cosine similarity scaled to 0-100 (float).
            - 'raw_cosine': Raw cosine similarity value in [-1, 1] (float).
    """
    if not student_text.strip() or not reference_text.strip():
        return {
            "similarity_score": 0.0,
            "raw_cosine": 0.0
        }
        
    try:
        model = get_sbert_model()
        
        embeddings = model.encode([student_text, reference_text], convert_to_tensor=True)
        
        cos_sim = util.cos_sim(embeddings[0], embeddings[1])
        raw_val = float(cos_sim.cpu().numpy()[0][0])
        
        lower_bound = 0.2
        upper_bound = 0.95
        
        if raw_val <= lower_bound:
            scaled_score = 0.0
        elif raw_val >= upper_bound:
            scaled_score = 100.0
        else:
            scaled_score = ((raw_val - lower_bound) / (upper_bound - lower_bound)) * 100.0
            
        return {
            "similarity_score": round(float(scaled_score), 2),
            "raw_cosine": round(raw_val, 4)
        }
    except Exception as e:
        print(f"Error calculating semantic similarity: {e}")
        return {
            "similarity_score": 0.0,
            "raw_cosine": 0.0
        }
