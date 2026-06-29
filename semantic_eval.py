from sentence_transformers import SentenceTransformer, util
import numpy as np
import streamlit as st
import config

logger = config.logger

_sbert_model = None

@st.cache_resource(max_entries=1)
def get_sbert_model(model_name="all-MiniLM-L6-v2"):
    """
    Lazy loads and caches the Sentence-Transformer model using Streamlit's cache_resource.
    'all-MiniLM-L6-v2' is very fast, accurate, and has a small footprint (~80MB).
    """
    logger.info(f"Loading Sentence-BERT model '{model_name}'...")
    model = SentenceTransformer(model_name)
    logger.info("Sentence-BERT model loaded successfully.")
    return model

@st.cache_resource
def get_reference_embedding(reference_text):
    """
    Generates and caches the semantic embedding for the static reference concepts.
    """
    model = get_sbert_model()
    return model.encode(reference_text, convert_to_tensor=True)

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
        
        # Encode student explanation (dynamic, calculated per request)
        student_emb = model.encode(student_text, convert_to_tensor=True)
        
        # Retrieve cached reference embedding
        ref_emb = get_reference_embedding(reference_text)
        
        cos_sim = util.cos_sim(student_emb, ref_emb)
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
        logger.error(f"Error calculating semantic similarity: {e}")
        return {
            "similarity_score": 0.0,
            "raw_cosine": 0.0
        }
