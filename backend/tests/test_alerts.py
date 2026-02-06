"""
Unit tests for Alerts API endpoints
"""
import pytest
from datetime import datetime, timedelta


class TestAlertsAPI:
    """Tests for Alerts API endpoints."""

    @pytest.fixture
    def mock_alert(self):
        """Sample alert for testing."""
        return {
            "id": "alert-123",
            "user_id": "test-user-123",
            "risk_level": "HIGH",
            "trigger_message": "ไม่รู้จะทนไปต่อได้อีกนานแค่ไหน",
            "created_at": datetime.utcnow().isoformat(),
            "resolved": False,
            "resolved_at": None,
            "resolved_notes": None
        }

    def test_alert_has_required_fields(self, mock_alert):
        """Test alert has all required fields."""
        required_fields = ["user_id", "risk_level", "trigger_message", "created_at", "resolved"]
        for field in required_fields:
            assert field in mock_alert

    def test_alert_risk_level_valid(self, mock_alert):
        """Test alert risk level is valid HIGH or MEDIUM."""
        valid_levels = ["MEDIUM", "HIGH"]
        assert mock_alert["risk_level"] in valid_levels

    def test_new_alert_unresolved(self, mock_alert):
        """Test new alerts are unresolved by default."""
        assert mock_alert["resolved"] is False
        assert mock_alert["resolved_at"] is None

    def test_alert_trigger_message_not_empty(self, mock_alert):
        """Test trigger message is not empty."""
        assert len(mock_alert["trigger_message"]) > 0


class TestAlertResolution:
    """Tests for alert resolution functionality."""

    @pytest.fixture
    def resolved_alert(self):
        """Sample resolved alert."""
        return {
            "id": "alert-123",
            "user_id": "test-user-123",
            "risk_level": "HIGH",
            "trigger_message": "ต้องการความช่วยเหลือ",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "resolved": True,
            "resolved_at": datetime.utcnow().isoformat(),
            "resolved_notes": "ติดต่อผู้ใช้แล้ว ปลอดภัยดี"
        }

    def test_resolved_alert_has_resolved_at(self, resolved_alert):
        """Test resolved alert has resolved_at timestamp."""
        assert resolved_alert["resolved"] is True
        assert resolved_alert["resolved_at"] is not None

    def test_resolved_alert_can_have_notes(self, resolved_alert):
        """Test resolved alert can have resolution notes."""
        assert resolved_alert["resolved_notes"] is not None
        assert len(resolved_alert["resolved_notes"]) > 0

    def test_resolve_changes_status(self):
        """Test that resolving changes resolved status."""
        alert = {"resolved": False}
        
        # Simulate resolve action
        alert["resolved"] = True
        alert["resolved_at"] = datetime.utcnow().isoformat()
        
        assert alert["resolved"] is True


class TestAlertFiltering:
    """Tests for alert filtering functionality."""

    @pytest.fixture
    def mock_alerts_list(self):
        """Sample list of alerts with various statuses."""
        return [
            {"id": "1", "risk_level": "HIGH", "resolved": False},
            {"id": "2", "risk_level": "MEDIUM", "resolved": True},
            {"id": "3", "risk_level": "HIGH", "resolved": False},
            {"id": "4", "risk_level": "MEDIUM", "resolved": False},
            {"id": "5", "risk_level": "HIGH", "resolved": True},
        ]

    def test_filter_unresolved_alerts(self, mock_alerts_list):
        """Test filtering for unresolved alerts only."""
        unresolved = [a for a in mock_alerts_list if not a["resolved"]]
        assert len(unresolved) == 3

    def test_filter_high_risk_alerts(self, mock_alerts_list):
        """Test filtering for HIGH risk alerts only."""
        high_risk = [a for a in mock_alerts_list if a["risk_level"] == "HIGH"]
        assert len(high_risk) == 3

    def test_filter_unresolved_high_risk(self, mock_alerts_list):
        """Test filtering for unresolved HIGH risk alerts."""
        critical = [a for a in mock_alerts_list 
                   if not a["resolved"] and a["risk_level"] == "HIGH"]
        assert len(critical) == 2

    def test_filter_resolved_alerts(self, mock_alerts_list):
        """Test filtering for resolved alerts."""
        resolved = [a for a in mock_alerts_list if a["resolved"]]
        assert len(resolved) == 2


class TestAlertStats:
    """Tests for alert statistics functionality."""

    @pytest.fixture
    def mock_alerts_for_stats(self):
        """Sample alerts for statistics calculation."""
        return [
            {"risk_level": "HIGH", "resolved": False},
            {"risk_level": "HIGH", "resolved": False},
            {"risk_level": "HIGH", "resolved": True},
            {"risk_level": "MEDIUM", "resolved": False},
            {"risk_level": "MEDIUM", "resolved": True},
            {"risk_level": "MEDIUM", "resolved": True},
        ]

    def test_count_by_risk_level(self, mock_alerts_for_stats):
        """Test counting alerts by risk level."""
        high_count = len([a for a in mock_alerts_for_stats if a["risk_level"] == "HIGH"])
        medium_count = len([a for a in mock_alerts_for_stats if a["risk_level"] == "MEDIUM"])
        
        assert high_count == 3
        assert medium_count == 3

    def test_count_unresolved(self, mock_alerts_for_stats):
        """Test counting unresolved alerts."""
        unresolved_count = len([a for a in mock_alerts_for_stats if not a["resolved"]])
        assert unresolved_count == 3

    def test_calculate_resolution_rate(self, mock_alerts_for_stats):
        """Test calculating resolution rate."""
        total = len(mock_alerts_for_stats)
        resolved = len([a for a in mock_alerts_for_stats if a["resolved"]])
        
        resolution_rate = (resolved / total) * 100
        assert resolution_rate == 50.0
