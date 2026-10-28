"""The release version must match in every file that declares it."""

import ast
import os
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE_KEYS = {"CFBundleVersion", "CFBundleShortVersionString"}


def _pyproject_version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["tool"]["poetry"]["version"]


def _package_version() -> str:
    tree = ast.parse((ROOT / "src" / "selladomx" / "__init__.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("__version__ not found in selladomx/__init__.py")


def _spec_versions() -> set[str]:
    """Evaluate the CFBundle*Version values in selladomx.spec.

    Values may be string literals or APP_VERSION, which the spec computes with
    read_app_version(); that function is executed from the repo root.
    """
    tree = ast.parse((ROOT / "selladomx.spec").read_text())
    namespace = {"ast": ast}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "read_app_version":
            exec(compile(ast.Module([node], []), "selladomx.spec", "exec"), namespace)

    versions = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and key.value in BUNDLE_KEYS):
                continue
            if isinstance(value, ast.Name) and value.id == "APP_VERSION":
                cwd = os.getcwd()
                os.chdir(ROOT)
                try:
                    versions[key.value] = namespace["read_app_version"]()
                finally:
                    os.chdir(cwd)
            else:
                versions[key.value] = ast.literal_eval(value)
    assert set(versions) == BUNDLE_KEYS, f"Missing in selladomx.spec: {versions}"
    return set(versions.values())


def _metainfo_latest_release() -> str:
    root = ET.parse(ROOT / "com.selladomx.SelladoMX.metainfo.xml").getroot()
    releases = root.findall("./releases/release")
    assert releases, "No <release> entries in metainfo"
    return releases[0].get("version")


def test_versions_match():
    expected = _pyproject_version()
    assert _package_version() == expected
    assert _spec_versions() == {expected}
    assert _metainfo_latest_release() == expected
