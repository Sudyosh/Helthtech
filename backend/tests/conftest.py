"""
Pytest configuration and shared fixtures for backend tests.
"""
import pytest
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test-user-12345"


@pytest.fixture
def sample_thai_message():
    """Sample Thai message for testing."""
    return "วันนี้รู้สึกเครียดมาก"


@pytest.fixture
def sample_english_message():
    """Sample English message for testing."""
    return "I'm feeling stressed today"


@pytest.fixture
def high_risk_messages():
    """Sample high-risk messages for testing."""
    return [
        "I want to kill myself",
        "I don't want to live anymore",
        "I want to hurt myself",
        "ฉันอยากตาย",
        "ไม่อยากมีชีวิตอยู่"
    ]


@pytest.fixture
def safe_messages():
    """Sample safe messages for testing."""
    return [
        "I'm having a good day",
        "วันนี้รู้สึกดี",
        "Feeling stressed about exams",
        "เครียดเรื่องเรียน",
        "Thanks for listening"
    ]
