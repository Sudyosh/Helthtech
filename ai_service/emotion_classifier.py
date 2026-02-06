"""
Emotion Classifier using HuggingFace models
Classifies text into emotional categories
"""
from transformers import pipeline
from typing import Optional
import os

# Global classifier (lazy loaded)
_emotion_classifier = None


def get_classifier():
    """Get or initialize the emotion classifier."""
    global _emotion_classifier
    
    if _emotion_classifier is None:
        try:
            # Use a lightweight emotion model
            _emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=1
            )
        except Exception as e:
            print(f"⚠️ Could not load emotion model: {e}")
            _emotion_classifier = "fallback"
    
    return _emotion_classifier


def classify_emotion(text: str) -> dict:
    """
    Classify the emotion in the given text.
    
    Args:
        text: Input text to classify
        
    Returns:
        dict with 'emotion' and 'confidence' keys
        
    Possible emotions: anger, disgust, fear, joy, neutral, sadness, surprise
    """
    if not text or not text.strip():
        return {"emotion": "neutral", "confidence": 0.0}
    
    classifier = get_classifier()
    
    if classifier == "fallback":
        # Fallback: simple keyword-based classification
        return _fallback_classify(text)
    
    try:
        # Limit text length for performance
        truncated_text = text[:512]
        results = classifier(truncated_text)
        
        if results and len(results) > 0:
            # Results are nested: [[{'label': 'joy', 'score': 0.95}]]
            top_result = results[0][0] if isinstance(results[0], list) else results[0]
            return {
                "emotion": top_result["label"].lower(),
                "confidence": round(top_result["score"], 4)
            }
    except Exception as e:
        print(f"⚠️ Error classifying emotion: {e}")
    
    return _fallback_classify(text)


def _fallback_classify(text: str) -> dict:
    """Simple keyword-based fallback classification."""
    text_lower = text.lower()
    
    # Emotion keyword mappings
    emotion_keywords = {
        "joy": ["happy", "glad", "excited", "wonderful", "great", "love", "amazing", "fantastic", "good"],
        "sadness": ["sad", "unhappy", "depressed", "down", "miserable", "lonely", "hopeless", "crying", "tears"],
        "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "hate", "pissed"],
        "fear": ["scared", "afraid", "terrified", "anxious", "worried", "nervous", "panic"],
        "surprise": ["surprised", "shocked", "amazed", "unexpected", "wow"],
        "disgust": ["disgusted", "gross", "sick", "revolting"]
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return {"emotion": emotion, "confidence": 0.6}
    
    return {"emotion": "neutral", "confidence": 0.5}


# Emotion severity mapping for risk assessment
EMOTION_SEVERITY = {
    "joy": 0,
    "surprise": 1,
    "neutral": 2,
    "anger": 3,
    "disgust": 3,
    "fear": 4,
    "sadness": 5
}


def get_emotion_severity(emotion: str) -> int:
    """Get severity score for an emotion (0-5, higher = more concerning)."""
    return EMOTION_SEVERITY.get(emotion.lower(), 2)
