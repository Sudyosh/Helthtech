"""
Sentiment Analyzer
Analyzes text sentiment polarity and intensity
"""
from transformers import pipeline
from typing import Optional

# Global analyzer (lazy loaded)
_sentiment_analyzer = None


def get_analyzer():
    """Get or initialize the sentiment analyzer."""
    global _sentiment_analyzer
    
    if _sentiment_analyzer is None:
        try:
            _sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            print(f"⚠️ Could not load sentiment model: {e}")
            _sentiment_analyzer = "fallback"
    
    return _sentiment_analyzer


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of the given text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        dict with 'score' (-1 to 1) and 'polarity' (positive/negative/neutral)
    """
    if not text or not text.strip():
        return {"score": 0.0, "polarity": "neutral"}
    
    analyzer = get_analyzer()
    
    if analyzer == "fallback":
        return _fallback_analyze(text)
    
    try:
        # Limit text length
        truncated_text = text[:512]
        results = analyzer(truncated_text)
        
        if results and len(results) > 0:
            result = results[0]
            label = result["label"].upper()
            score = result["score"]
            
            # Convert to -1 to 1 scale
            if label == "POSITIVE":
                sentiment_score = score
                polarity = "positive"
            else:
                sentiment_score = -score
                polarity = "negative"
            
            # Adjust for near-neutral scores
            if abs(sentiment_score) < 0.3:
                polarity = "neutral"
            
            return {
                "score": round(sentiment_score, 4),
                "polarity": polarity
            }
    except Exception as e:
        print(f"⚠️ Error analyzing sentiment: {e}")
    
    return _fallback_analyze(text)


def _fallback_analyze(text: str) -> dict:
    """Simple keyword-based fallback sentiment analysis."""
    text_lower = text.lower()
    
    positive_words = [
        "good", "great", "happy", "love", "wonderful", "amazing", 
        "fantastic", "excellent", "best", "beautiful", "joy", "hope",
        "better", "improve", "grateful", "thanks", "helpful"
    ]
    
    negative_words = [
        "bad", "terrible", "sad", "hate", "awful", "horrible", 
        "worst", "pain", "hurt", "lonely", "hopeless", "scared",
        "angry", "frustrated", "tired", "exhausted", "stressed",
        "anxious", "worried", "depressed", "miserable"
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total = positive_count + negative_count
    
    if total == 0:
        return {"score": 0.0, "polarity": "neutral"}
    
    score = (positive_count - negative_count) / max(total, 1)
    
    if score > 0.2:
        polarity = "positive"
    elif score < -0.2:
        polarity = "negative"
    else:
        polarity = "neutral"
    
    return {"score": round(score, 4), "polarity": polarity}


def get_sentiment_intensity(score: float) -> str:
    """Get intensity level from sentiment score."""
    abs_score = abs(score)
    
    if abs_score >= 0.8:
        return "very_strong"
    elif abs_score >= 0.6:
        return "strong"
    elif abs_score >= 0.4:
        return "moderate"
    elif abs_score >= 0.2:
        return "mild"
    else:
        return "neutral"
