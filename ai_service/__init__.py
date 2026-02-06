"""
AI Service Package
Mental health companion AI modules
"""
from .emotion_classifier import classify_emotion, get_emotion_severity
from .sentiment_analyzer import analyze_sentiment, get_sentiment_intensity
from .risk_detector import detect_risk, check_for_crisis, get_risk_response_guidance
from .llm_companion import generate_response

__all__ = [
    "classify_emotion",
    "get_emotion_severity",
    "analyze_sentiment", 
    "get_sentiment_intensity",
    "detect_risk",
    "check_for_crisis",
    "get_risk_response_guidance",
    "generate_response"
]
