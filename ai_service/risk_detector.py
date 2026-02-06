"""
Risk Detector
Rule-based risk detection for mental health concerns
"""
from typing import Optional, List
import re


# High-risk keywords and phrases that require immediate attention
HIGH_RISK_KEYWORDS = [
    "kill myself",
    "want to die",
    "hurt myself",
    "end my life",
    "suicide",
    "self harm",
    "self-harm",
    "cut myself",
    "don't want to live",
    "don't want to be alive",
    "better off dead",
    "no reason to live",
    "end it all",
    "take my own life",
    "overdose",
]

# Medium-risk patterns indicating distress
MEDIUM_RISK_PATTERNS = [
    r"feel(?:ing)?\s+(?:so\s+)?(?:hopeless|worthless|empty|numb)",
    r"(?:nobody|no\s*one)\s+(?:cares|loves|understands)",
    r"can'?t\s+(?:go on|take it|handle|cope)",
    r"(?:hate|despise)\s+myself",
    r"(?:always|constantly)\s+(?:sad|depressed|anxious)",
    r"(?:nothing|life)\s+(?:matters|has meaning)",
    r"(?:trapped|stuck)\s+(?:in|with)",
    r"(?:never|won't)\s+get\s+better",
    r"burden\s+(?:to|on)\s+(?:everyone|others|family)",
]

# Concerning but lower priority patterns
LOW_RISK_PATTERNS = [
    r"(?:stressed|overwhelmed|exhausted)",
    r"(?:can'?t|unable\s+to)\s+sleep",
    r"(?:lonely|isolated|alone)",
    r"(?:worried|anxious)\s+about",
    r"feeling\s+(?:down|low|blue)",
]


def detect_risk(
    text: str, 
    emotion: Optional[str] = None, 
    sentiment: Optional[float] = None
) -> dict:
    """
    Detect risk level from text and optional emotion/sentiment data.
    
    Args:
        text: The message text to analyze
        emotion: Optional emotion label from classifier
        sentiment: Optional sentiment score (-1 to 1)
        
    Returns:
        dict with 'level' (LOW/MEDIUM/HIGH), 'score' (0-100), and 'factors'
    """
    if not text:
        return {"level": "LOW", "score": 0.0, "factors": []}
    
    text_lower = text.lower()
    factors = []
    base_score = 0.0
    
    # Check for HIGH risk keywords (immediate flags)
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            factors.append(f"High-risk keyword detected: '{keyword}'")
            base_score = max(base_score, 85.0)
    
    # Check for MEDIUM risk patterns
    for pattern in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, text_lower):
            match = re.search(pattern, text_lower)
            factors.append(f"Distress pattern detected")
            base_score = max(base_score, 55.0)
    
    # Check for LOW risk patterns
    for pattern in LOW_RISK_PATTERNS:
        if re.search(pattern, text_lower):
            if base_score < 40:
                base_score = max(base_score, 25.0)
            factors.append("Stress indicator detected")
            break  # Only add once
    
    # Adjust based on emotion
    if emotion:
        emotion_adjustments = {
            "sadness": 15,
            "fear": 12,
            "anger": 8,
            "disgust": 5,
            "surprise": 0,
            "neutral": 0,
            "joy": -10
        }
        adjustment = emotion_adjustments.get(emotion.lower(), 0)
        if adjustment != 0:
            base_score += adjustment
            if adjustment > 0:
                factors.append(f"Negative emotion detected: {emotion}")
    
    # Adjust based on sentiment
    if sentiment is not None:
        if sentiment < -0.6:
            base_score += 10
            factors.append("Very negative sentiment")
        elif sentiment < -0.3:
            base_score += 5
            factors.append("Negative sentiment")
    
    # Ensure score is in valid range
    final_score = max(0, min(100, base_score))
    
    # Determine risk level
    if final_score >= 70:
        level = "HIGH"
    elif final_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    # Deduplicate factors
    factors = list(dict.fromkeys(factors))
    
    return {
        "level": level,
        "score": round(final_score, 1),
        "factors": factors
    }


def get_risk_response_guidance(risk_level: str) -> dict:
    """
    Get guidance for AI response based on risk level.
    
    Returns:
        dict with 'tone', 'priorities', and 'resources' fields
    """
    if risk_level == "HIGH":
        return {
            "tone": "calm, supportive, and non-judgmental",
            "priorities": [
                "Acknowledge their feelings without dismissing them",
                "Express care and concern",
                "Gently encourage professional support",
                "Avoid leaving them feeling alone"
            ],
            "suggest_resources": True,
            "response_style": "empathetic_urgent"
        }
    elif risk_level == "MEDIUM":
        return {
            "tone": "warm, validating, and supportive",
            "priorities": [
                "Validate their emotions",
                "Explore their feelings with open questions",
                "Offer coping strategies if appropriate",
                "Maintain connection"
            ],
            "suggest_resources": False,
            "response_style": "empathetic_supportive"
        }
    else:
        return {
            "tone": "friendly, curious, and encouraging",
            "priorities": [
                "Engage naturally",
                "Show interest in their experiences",
                "Provide emotional support",
                "Encourage self-reflection"
            ],
            "suggest_resources": False,
            "response_style": "conversational"
        }


def check_for_crisis(text: str) -> bool:
    """
    Quick check if text indicates an immediate crisis.
    
    Returns:
        True if crisis indicators present
    """
    crisis_indicators = [
        "kill myself",
        "suicide",
        "want to die",
        "going to hurt myself",
        "end my life",
        "overdose",
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in crisis_indicators)
