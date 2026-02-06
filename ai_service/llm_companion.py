"""
LLM Companion
AI companion response generation using LLM API
"""
import os
from typing import Optional
from openai import AsyncOpenAI
from .risk_detector import get_risk_response_guidance


# Initialize OpenAI client (lazy)
_client = None


def get_client():
    """Get or initialize the OpenAI client."""
    global _client
    
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key != "your_openai_api_key_here":
            _client = AsyncOpenAI(api_key=api_key)
        else:
            _client = "mock"
    
    return _client


# System prompt for the AI companion
COMPANION_SYSTEM_PROMPT = """You are a supportive AI companion for teenagers. Your role is to provide emotional support through empathetic conversation.

CORE PRINCIPLES:
1. NEVER provide medical diagnoses or clinical advice
2. ALWAYS use non-judgmental, validating language
3. Practice reflective listening - mirror back what you hear
4. Ask open-ended questions to encourage sharing
5. Validate emotions before suggesting solutions
6. Be warm, genuine, and age-appropriate

RESPONSE STYLE:
- Keep responses concise (2-4 sentences typically)
- Use a conversational, friendly tone
- Avoid being preachy or lecturing
- Show you're genuinely listening

EXAMPLE PHRASES:
- "That sounds really difficult."
- "I can understand why you'd feel that way."
- "Would you like to tell me more about that?"
- "It's okay to feel this way."
- "I'm here to listen."

IMPORTANT: You are NOT a therapist. If someone shares serious concerns, acknowledge them supportively but never minimize, and gently encourage talking to a trusted adult or professional."""

HIGH_RISK_ADDENDUM = """
CRITICAL: The user may be in distress. Respond with extra care:
- Stay calm and present
- Don't panic or overreact in your response
- Acknowledge their pain without judgment
- Gently encourage reaching out to someone they trust
- Remind them that support is available
- Do NOT leave them feeling alone or dismissed

If appropriate, you may mention that talking to a school counselor, trusted adult, or calling a helpline like 988 (Suicide & Crisis Lifeline) can help."""


async def generate_response(
    message: str,
    emotion: Optional[str] = None,
    risk_level: Optional[str] = None,
    conversation_history: Optional[list] = None
) -> str:
    """
    Generate an empathetic AI companion response.
    
    Args:
        message: The user's message
        emotion: Detected emotion (optional)
        risk_level: Risk level assessment (optional)
        conversation_history: Previous messages for context (optional)
        
    Returns:
        AI companion response string
    """
    client = get_client()
    
    # Use mock responses if no API key
    if client == "mock":
        return _generate_mock_response(message, emotion, risk_level)
    
    # Build system prompt based on risk level
    system_prompt = COMPANION_SYSTEM_PROMPT
    if risk_level == "HIGH":
        system_prompt += "\n\n" + HIGH_RISK_ADDENDUM
    
    # Get response guidance
    guidance = get_risk_response_guidance(risk_level or "LOW")
    
    # Build messages array
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("message", "")
            })
    
    # Add current message with context
    context_note = ""
    if emotion and emotion != "neutral":
        context_note = f"[User appears to be feeling {emotion}] "
    
    messages.append({
        "role": "user",
        "content": context_note + message
    })
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
            presence_penalty=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️ Error generating LLM response: {e}")
        return _generate_mock_response(message, emotion, risk_level)


def _generate_mock_response(
    message: str,
    emotion: Optional[str] = None,
    risk_level: Optional[str] = None
) -> str:
    """Generate a mock response when LLM is unavailable."""
    
    message_lower = message.lower()
    
    # High risk response
    if risk_level == "HIGH":
        return (
            "I hear that you're going through something really painful right now. "
            "I want you to know that you're not alone, and what you're feeling matters. "
            "Would it be possible to talk to someone you trust about this? "
            "I'm here to listen, and I care about you."
        )
    
    # Greeting responses
    if any(word in message_lower for word in ["hi", "hello", "hey"]):
        return (
            "Hey! It's good to hear from you. "
            "How are you feeling today? I'm here if you want to talk about anything."
        )
    
    # Responses based on detected emotion
    if emotion == "sadness":
        return (
            "It sounds like you're going through a tough time. "
            "I'm really sorry you're feeling this way. "
            "Would you like to tell me more about what's been going on?"
        )
    
    if emotion == "fear" or emotion == "anxiety":
        return (
            "That sounds really stressful. It's completely understandable to feel worried. "
            "What's been weighing on your mind the most?"
        )
    
    if emotion == "anger":
        return (
            "I can hear that you're frustrated. Those feelings are valid. "
            "What happened that's got you feeling this way?"
        )
    
    if emotion == "joy":
        return (
            "That's wonderful to hear! It sounds like something good is happening. "
            "I'd love to hear more about it!"
        )
    
    # Medium risk / distress
    if risk_level == "MEDIUM":
        return (
            "It sounds like things have been really hard lately. "
            "I want you to know that your feelings are valid, and it's okay to not be okay sometimes. "
            "What would feel helpful to talk about right now?"
        )
    
    # Default empathetic response
    return (
        "I hear you. That sounds like something worth exploring. "
        "Would you like to tell me more about how you're feeling?"
    )


# Response templates for common scenarios
RESPONSE_TEMPLATES = {
    "greeting": [
        "Hey! Good to see you. How's everything going?",
        "Hi there! What's on your mind today?",
        "Hello! I'm here to chat whenever you're ready."
    ],
    "thanks": [
        "Of course! I'm always here to listen.",
        "Happy to help. Remember, you can talk to me anytime.",
        "You're welcome. Keep taking care of yourself!"
    ],
    "goodbye": [
        "Take care of yourself! I'm here whenever you need to talk.",
        "Goodbye for now. Remember, it's okay to reach out anytime.",
        "See you! Wishing you a good day ahead."
    ]
}
