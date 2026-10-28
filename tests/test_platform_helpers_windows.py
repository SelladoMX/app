"""Windows URL-handler checks, run on any OS with a fake winreg"""

import sys
import types

import pytest

from selladomx.utils import platform_helpers as ph

INSTALLED = r"C:\Users\Ana\AppData\Local\Programs\SelladoMX\selladomx.exe"
PORTABLE = r"C:\Users\Ana\Downloads\selladomx\selladomx.exe"
OLD_PORTABLE = r"C:\Users\Ana\Desktop\SelladoMX-0.4.1\selladomx.exe"


def command(exe):
    return f'"{exe}" "%1"'


# ============================================================================
# should_update_url_handler
# ============================================================================


@pytest.mark.parametrize(
    "current, registered, installed, existing, expected",
    [
        # Nothing registered: any copy takes the handler
        (INSTALLED, None, INSTALLED, set(), True),
        (PORTABLE, None, None, set(), True),
        # Already pointing at this copy (case-insensitive)
        (INSTALLED, command(INSTALLED), INSTALLED, {INSTALLED}, False),
        (PORTABLE, command(PORTABLE.upper()), None, {PORTABLE}, False),
        # Installed copy takes it from a portable copy, even a live one
        (INSTALLED, command(PORTABLE), INSTALLED, {PORTABLE, INSTALLED}, True),
        (INSTALLED.lower(), command(PORTABLE), INSTALLED, {PORTABLE}, True),
        # Portable copy leaves a valid installed copy alone
        (PORTABLE, command(INSTALLED), INSTALLED, {INSTALLED}, False),
        # ...and another portable copy that still exists
        (PORTABLE, command(OLD_PORTABLE), None, {OLD_PORTABLE}, False),
        # Portable copy takes it when the registered exe is gone
        (PORTABLE, command(OLD_PORTABLE), None, set(), True),
        (PORTABLE, command(INSTALLED), INSTALLED, set(), True),
        # Unquoted or empty commands
        (PORTABLE, f"{OLD_PORTABLE} %1", None, {OLD_PORTABLE}, False),
        (PORTABLE, "", None, set(), True),
    ],
)
def test_should_update_url_handler(
    monkeypatch, current, registered, installed, existing, expected
):
    monkeypatch.setattr(ph, "_exe_exists", lambda p: p in existing)

    assert ph.should_update_url_handler(current, registered, installed) is expected


# ============================================================================
# ensure_url_scheme_windows with a fake registry
# ============================================================================


class FakeKey:
    def __init__(self, registry, path):
        self.registry = registry
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def make_fake_winreg(registry):
    """Build a winreg stand-in backed by {key path (lowercase): {name: value}}."""
    mod = types.ModuleType("winreg")
    mod.HKEY_CURRENT_USER = "HKCU"
    mod.REG_SZ = 1

    def open_key(root, path, *args):
        if path.lower() not in registry:
            raise FileNotFoundError(path)
        return FakeKey(registry, path.lower())

    def create_key(root, path):
        registry.setdefault(path.lower(), {})
        return FakeKey(registry, path.lower())

    def query_value_ex(key, name):
        values = registry[key.path]
        if name not in values:
            raise FileNotFoundError(name)
        return values[name], mod.REG_SZ

    def set_value_ex(key, name, reserved, kind, value):
        registry[key.path][name] = value

    # QueryValue and SetValue work on the default value of a subkey, and
    # QueryValue returns a plain string, unlike QueryValueEx's (value, type).
    def subkey_path(key, sub_key):
        return f"{key.path}\\{sub_key.lower()}" if sub_key else key.path

    def query_value(key, sub_key):
        return registry.get(subkey_path(key, sub_key), {}).get("", "")

    def set_value(key, sub_key, kind, value):
        registry.setdefault(subkey_path(key, sub_key), {})[""] = value

    mod.OpenKey = open_key
    mod.CreateKey = create_key
    mod.QueryValue = query_value
    mod.QueryValueEx = query_value_ex
    mod.SetValue = set_value
    mod.SetValueEx = set_value_ex
    return mod


COMMAND_KEY = r"software\classes\selladomx\shell\open\command"
UNINSTALL_KEY = (
    r"software\microsoft\windows\currentversion\uninstall"
    r"\{4285fac5-53b6-436f-89b4-a58266d49505}_is1"
)


@pytest.fixture
def fake_windows(monkeypatch):
    registry = {}
    existing = set()
    monkeypatch.setitem(sys.modules, "winreg", make_fake_winreg(registry))
    monkeypatch.setattr(ph.sys, "platform", "win32")
    monkeypatch.setattr(ph, "_exe_exists", lambda p: p in existing)

    def run_as(exe):
        monkeypatch.setattr(ph, "_current_exe", lambda: exe)
        return ph.ensure_url_scheme_windows()

    return registry, existing, run_as


def install(registry, existing):
    location = INSTALLED.rsplit("\\", 1)[0] + "\\"
    registry[UNINSTALL_KEY] = {"InstallLocation": location}
    registry[COMMAND_KEY] = {"": command(INSTALLED)}
    existing.add(INSTALLED)


def test_portable_copy_registers_when_nothing_is_registered(fake_windows):
    registry, _, run_as = fake_windows

    assert run_as(PORTABLE) is True

    assert registry[COMMAND_KEY][""] == command(PORTABLE)
    assert registry[r"software\classes\selladomx"] == {
        "": "URL:SelladoMX Protocol",
        "URL Protocol": "",
    }
    assert registry[r"software\classes\selladomx\defaulticon"][""] == (f"{PORTABLE},0")


def test_portable_copy_keeps_installed_handler(fake_windows):
    registry, existing, run_as = fake_windows
    install(registry, existing)

    assert run_as(PORTABLE) is True

    assert registry[COMMAND_KEY][""] == command(INSTALLED)


def test_installed_copy_reclaims_handler_from_portable(fake_windows):
    registry, existing, run_as = fake_windows
    install(registry, existing)
    registry[COMMAND_KEY][""] = command(OLD_PORTABLE)
    existing.add(OLD_PORTABLE)

    assert run_as(INSTALLED) is True

    assert registry[COMMAND_KEY][""] == command(INSTALLED)


def test_portable_copy_replaces_deleted_old_copy(fake_windows):
    registry, _, run_as = fake_windows
    registry[COMMAND_KEY] = {"": command(OLD_PORTABLE)}

    assert run_as(PORTABLE) is True

    assert registry[COMMAND_KEY][""] == command(PORTABLE)


def test_registry_write_failure_returns_false(fake_windows, monkeypatch):
    _, _, run_as = fake_windows

    def denied(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(sys.modules["winreg"], "CreateKey", denied)

    assert run_as(PORTABLE) is False


def test_app_mutex_is_noop_off_windows(monkeypatch):
    monkeypatch.setattr(ph.sys, "platform", "darwin")
    monkeypatch.setattr(ph, "_app_mutex", None)

    assert ph.create_app_mutex() is None


def test_existing_handler_for_this_copy_is_read(fake_windows):
    """Regression for 0.4.2, which unpacked QueryValue's plain string."""
    registry, _, run_as = fake_windows
    registry[COMMAND_KEY] = {"": command(PORTABLE)}

    assert run_as(PORTABLE) is True
    assert registry[COMMAND_KEY][""] == command(PORTABLE)


def test_frozen_exe_path_is_registered(fake_windows, monkeypatch):
    registry, _, _ = fake_windows
    monkeypatch.setattr(ph.sys, "frozen", True, raising=False)
    monkeypatch.setattr(ph.sys, "executable", PORTABLE)

    assert ph.is_url_scheme_registered_windows() is False
    assert ph.register_url_scheme() is True
    # On a non-Windows test host abspath() prefixes the cwd to a C:\ path
    assert registry[COMMAND_KEY][""].endswith(f'{PORTABLE}" "%1"')
    assert ph.is_url_scheme_registered_windows() is True
