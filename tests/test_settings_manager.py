"""Tests for SettingsManager."""

from pathlib import Path

import pytest
from selladomx.utils.settings_manager import SettingsManager


@pytest.fixture
def settings_manager():
    """SettingsManager backed by the per-test settings dir from conftest."""
    return SettingsManager()


def test_settings_are_isolated(settings_manager, isolated_settings):
    """Settings are written under the test's tmp dir, not the user's profile."""
    settings_manager.mark_onboarding_completed()
    settings_manager.settings.sync()

    settings_file = Path(settings_manager.settings.fileName())
    assert settings_file.is_relative_to(isolated_settings)
    assert settings_file.exists()


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

    new_manager = SettingsManager()
    assert new_manager.has_completed_onboarding() is True
    assert new_manager.get_onboarding_version() == 1
