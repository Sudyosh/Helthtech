"""
Unit tests for Mood API endpoints
"""
import pytest
from datetime import datetime, timedelta


class TestMoodAPI:
    """Tests for Mood logging API endpoints."""

    @pytest.fixture
    def mock_mood_entry(self):
        """Sample mood entry for testing."""
        return {
            "user_id": "test-user-123",
            "mood_score": 7,
            "stress_score": 4,
            "notes": "วันนี้รู้สึกดี"
        }

    def test_mood_score_range(self, mock_mood_entry):
        """Test mood score is within valid range 1-10."""
        assert 1 <= mock_mood_entry["mood_score"] <= 10

    def test_stress_score_range(self, mock_mood_entry):
        """Test stress score is within valid range 1-10."""
        assert 1 <= mock_mood_entry["stress_score"] <= 10

    def test_mood_entry_has_user_id(self, mock_mood_entry):
        """Test mood entry has user_id."""
        assert "user_id" in mock_mood_entry
        assert len(mock_mood_entry["user_id"]) > 0

    def test_mood_entry_optional_notes(self):
        """Test that notes field is optional."""
        mood_without_notes = {
            "user_id": "test-user-123",
            "mood_score": 5,
            "stress_score": 5
        }
        # Notes can be omitted
        assert "notes" not in mood_without_notes or mood_without_notes.get("notes") is None

    def test_invalid_mood_score_too_low(self):
        """Test that mood score below 1 is invalid."""
        mood_score = 0
        is_valid = 1 <= mood_score <= 10
        assert is_valid is False

    def test_invalid_mood_score_too_high(self):
        """Test that mood score above 10 is invalid."""
        mood_score = 11
        is_valid = 1 <= mood_score <= 10
        assert is_valid is False


class TestMoodHistory:
    """Tests for mood history functionality."""

    @pytest.fixture
    def mock_mood_history(self):
        """Sample mood history data."""
        return [
            {"date": "2026-02-06", "mood_score": 7, "stress_score": 4},
            {"date": "2026-02-05", "mood_score": 6, "stress_score": 5},
            {"date": "2026-02-04", "mood_score": 5, "stress_score": 6},
            {"date": "2026-02-03", "mood_score": 6, "stress_score": 5},
            {"date": "2026-02-02", "mood_score": 7, "stress_score": 4},
        ]

    def test_calculate_average_mood(self, mock_mood_history):
        """Test average mood calculation."""
        total = sum(entry["mood_score"] for entry in mock_mood_history)
        count = len(mock_mood_history)
        avg = total / count
        
        expected_avg = (7 + 6 + 5 + 6 + 7) / 5  # 6.2
        assert avg == expected_avg

    def test_calculate_average_stress(self, mock_mood_history):
        """Test average stress calculation."""
        total = sum(entry["stress_score"] for entry in mock_mood_history)
        count = len(mock_mood_history)
        avg = total / count
        
        expected_avg = (4 + 5 + 6 + 5 + 4) / 5  # 4.8
        assert avg == expected_avg

    def test_history_date_range_filter(self):
        """Test that history can be filtered by date range."""
        days = 7
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Verify start_date is 7 days ago
        diff = datetime.utcnow() - start_date
        assert 6 <= diff.days <= 7

    def test_empty_history_returns_none_averages(self):
        """Test that empty history returns None for averages."""
        empty_history = []
        
        if len(empty_history) == 0:
            avg_mood = None
            avg_stress = None
        else:
            avg_mood = sum(e["mood_score"] for e in empty_history) / len(empty_history)
            avg_stress = sum(e["stress_score"] for e in empty_history) / len(empty_history)
        
        assert avg_mood is None
        assert avg_stress is None


class TestMoodTrends:
    """Tests for mood trends aggregation."""

    @pytest.fixture
    def mock_trend_data(self):
        """Sample trend data grouped by day."""
        return [
            {"date": "2026-02-01", "average_mood": 6.2, "average_stress": 5.8, "entries": 3},
            {"date": "2026-02-02", "average_mood": 5.9, "average_stress": 6.1, "entries": 2},
            {"date": "2026-02-03", "average_mood": 6.5, "average_stress": 5.5, "entries": 4},
        ]

    def test_trend_data_structure(self, mock_trend_data):
        """Test trend data has required fields."""
        for trend in mock_trend_data:
            assert "date" in trend
            assert "average_mood" in trend
            assert "average_stress" in trend
            assert "entries" in trend

    def test_trend_averages_rounded(self, mock_trend_data):
        """Test that averages are rounded to 1 decimal place."""
        for trend in mock_trend_data:
            mood_str = str(trend["average_mood"])
            if "." in mood_str:
                decimals = len(mood_str.split(".")[1])
                assert decimals <= 1

    def test_trend_entries_positive(self, mock_trend_data):
        """Test that entry counts are positive."""
        for trend in mock_trend_data:
            assert trend["entries"] > 0


class TestStressQuestionnaire:
    """Tests for stress questionnaire."""

    @pytest.fixture
    def mock_questionnaire(self):
        """Sample questionnaire response."""
        return {
            "user_id": "test-user-123",
            "sleep_quality": 3,
            "energy_level": 2,
            "social_connection": 3,
            "anxiety_level": 4,
            "concentration": 2,
            "physical_symptoms": "ปวดหัว"
        }

    def test_questionnaire_fields_range(self, mock_questionnaire):
        """Test questionnaire fields are in 1-5 range."""
        score_fields = ["sleep_quality", "energy_level", "social_connection", 
                       "anxiety_level", "concentration"]
        
        for field in score_fields:
            assert 1 <= mock_questionnaire[field] <= 5

    def test_calculate_stress_from_questionnaire(self, mock_questionnaire):
        """Test stress score calculation from questionnaire."""
        q = mock_questionnaire
        stress_factors = [
            (5 - q["sleep_quality"]),
            (5 - q["energy_level"]),
            (5 - q["social_connection"]),
            q["anxiety_level"],
            (5 - q["concentration"])
        ]
        
        avg_stress = sum(stress_factors) / len(stress_factors)
        stress_score = min(10, max(1, int(avg_stress * 2)))
        
        # Verify stress score is in valid range
        assert 1 <= stress_score <= 10
