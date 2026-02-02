"""Tests for SettingsManager."""
import pytest
from PySide6.QtCore import QSettings
from selladomx.utils.settings_manager import SettingsManager


@pytest.fixture
def settings_manager():
    """Create a SettingsManager instance for testing."""
    manager = SettingsManager()
    # Reset state before each test
    manager.reset_onboarding()
    manager.set_onboarding_version(0)
    yield manager
    # Cleanup after test
    manager.reset_onboarding()
    manager.set_onboarding_version(0)


def test_initial_state(settings_manager):
    """Test that onboarding is not completed initially."""
    assert settings_manager.has_completed_onboarding() is False
    assert settings_manager.get_onboarding_version() == 0


def test_mark_onboarding_completed(settings_manager):
    """Test marking onboarding as completed."""
    settings_manager.mark_onboarding_completed()
    assert settings_manager.has_completed_onboarding() is True


def test_reset_onboarding(settings_manager):
    """Test resetting onboarding status."""
    settings_manager.mark_onboarding_completed()
    assert settings_manager.has_completed_onboarding() is True

    settings_manager.reset_onboarding()
    assert settings_manager.has_completed_onboarding() is False


def test_onboarding_version(settings_manager):
    """Test onboarding version tracking."""
    assert settings_manager.get_onboarding_version() == 0

    settings_manager.set_onboarding_version(1)
    assert settings_manager.get_onboarding_version() == 1

    settings_manager.set_onboarding_version(2)
    assert settings_manager.get_onboarding_version() == 2


def test_persistence(settings_manager):
    """Test that settings persist across instances."""
    settings_manager.mark_onboarding_completed()
    settings_manager.set_onboarding_version(1)

    # Create new instance
    new_manager = SettingsManager()
    assert new_manager.has_completed_onboarding() is True
    assert new_manager.get_onboarding_version() == 1

    # Cleanup
    new_manager.reset_onboarding()
