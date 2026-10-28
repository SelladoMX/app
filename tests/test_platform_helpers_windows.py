"""Windows URL-handler checks, run on any OS with a fake winreg"""

import sys
import types

import pytest

from selladomx.utils import platform_helpers


class _Key:
    def __init__(self, store, path):
        self.store, self.path = store, path

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_winreg(store):
    """Mimic the winreg calls we use; QueryValue returns a plain string."""
    winreg = types.ModuleType("winreg")
    winreg.HKEY_CURRENT_USER = object()
    winreg.REG_SZ = 1

    def open_key(root, path):
        if path not in store:
            raise FileNotFoundError(path)
        return _Key(store, path)

    def create_key(root, path):
        store.setdefault(path, "")
        return _Key(store, path)

    winreg.OpenKey = open_key
    winreg.CreateKey = create_key
    winreg.QueryValue = lambda key, sub: key.store[key.path]
    winreg.SetValue = lambda key, sub, kind, value: key.store.__setitem__(
        key.path, value
    )
    winreg.SetValueEx = lambda key, name, reserved, kind, value: None
    return winreg


COMMAND_KEY = r"Software\Classes\selladomx\shell\open\command"


@pytest.fixture
def registry(monkeypatch):
    store = {}
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(store))
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Apps\SelladoMX\selladomx.exe")
    return store


def test_missing_handler_is_not_registered(registry):
    assert platform_helpers.is_url_scheme_registered_windows() is False


def test_handler_for_this_exe_is_registered(registry):
    registry[COMMAND_KEY] = platform_helpers._windows_handler_command()
    assert platform_helpers.is_url_scheme_registered_windows() is True


def test_handler_for_another_copy_is_rewritten(registry):
    registry[COMMAND_KEY] = r'"C:\Old\selladomx.exe" "%1"'

    assert platform_helpers.register_url_scheme() is True
    assert registry[COMMAND_KEY] == platform_helpers._windows_handler_command()
