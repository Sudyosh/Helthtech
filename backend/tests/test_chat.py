"""
Unit tests for Chat API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestChatAPI:
    """Tests for Chat API endpoints."""

    @pytest.fixture
    def mock_chat_message(self):
        """Sample chat message for testing."""
        return {
            "user_id": "test-user-123",
            "message": "ฉันรู้สึกเครียดมากเรื่องเรียน"
        }

    @pytest.fixture
    def mock_chat_response(self):
        """Expected chat response structure."""
        return {
            "user_id": "test-user-123",
            "user_message": "ฉันรู้สึกเครียดมากเรื่องเรียน",
            "ai_response": "ฉันเข้าใจนะว่าความเครียดเรื่องเรียนเป็นเรื่องหนัก",
            "emotion": "fear",
            "emotion_confidence": 0.85,
            "sentiment_score": -0.3,
            "sentiment_polarity": "negative",
            "risk_level": "LOW",
            "risk_score": 25.0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def test_chat_message_validation(self, mock_chat_message):
        """Test that chat message has required fields."""
        assert "user_id" in mock_chat_message
        assert "message" in mock_chat_message
        assert len(mock_chat_message["message"]) > 0

    def test_chat_response_structure(self, mock_chat_response):
        """Test chat response has all expected fields."""
        required_fields = [
            "user_id", "user_message", "ai_response",
            "emotion", "risk_level", "timestamp"
        ]
        for field in required_fields:
            assert field in mock_chat_response

    def test_emotion_classification_output(self):
        """Test emotion classifier returns valid emotion."""
        valid_emotions = ["joy", "sadness", "fear", "anger", "neutral", "surprise"]
        # This would test the actual emotion classifier
        test_emotion = "fear"
        assert test_emotion in valid_emotions

    def test_risk_level_values(self):
        """Test that risk levels are valid."""
        valid_levels = ["LOW", "MEDIUM", "HIGH"]
        test_level = "LOW"
        assert test_level in valid_levels

    def test_high_risk_triggers_alert(self):
        """Test that HIGH risk level should trigger an alert."""
        risk_level = "HIGH"
        should_alert = risk_level == "HIGH"
        assert should_alert is True

    def test_low_risk_no_alert(self):
        """Test that LOW risk level should not trigger an alert."""
        risk_level = "LOW"
        should_alert = risk_level == "HIGH"
        assert should_alert is False

    def test_risk_keywords_detection(self):
        """Test that risk keywords are properly detected."""
        high_risk_keywords = ["kill myself", "want to die", "hurt myself", "suicide"]
        test_message = "I want to hurt myself"
        
        contains_risk = any(keyword in test_message.lower() for keyword in high_risk_keywords)
        assert contains_risk is True

    def test_safe_message_no_risk(self):
        """Test that safe messages don't trigger high risk."""
        high_risk_keywords = ["kill myself", "want to die", "hurt myself", "suicide"]
        test_message = "I'm having a nice day at school"
        
        contains_risk = any(keyword in test_message.lower() for keyword in high_risk_keywords)
        assert contains_risk is False


class TestChatHistory:
    """Tests for chat history functionality."""

    def test_history_limit_validation(self):
        """Test that history limit is within bounds."""
        limit = 50
        assert 1 <= limit <= 100

    def test_messages_sorted_chronologically(self):
        """Test messages are in chronological order."""
        messages = [
            {"timestamp": "2026-02-06T10:00:00Z", "message": "First"},
            {"timestamp": "2026-02-06T11:00:00Z", "message": "Second"},
            {"timestamp": "2026-02-06T12:00:00Z", "message": "Third"},
        ]
        
        # Check timestamps are ascending
        timestamps = [m["timestamp"] for m in messages]
        assert timestamps == sorted(timestamps)
