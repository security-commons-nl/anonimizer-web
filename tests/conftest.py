"""Test-setup: mock anonimizer-core modules zodat tests draaien zonder de
core-repo te clonen. In Docker komt anonimizer-core mee via ANONIMIZER_PATH,
maar in CI willen we de web-app geisoleerd kunnen testen.
"""
import sys
import types

import pytest


def _install_mock_module(name: str, **attrs) -> types.ModuleType:
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    sys.modules[name] = mod
    return mod


# Mock state die per-test gereset wordt via de mock_anonimizer fixture.
_mock_state: dict = {
    "to_markdown": lambda pad: "# Mock document\n\nGeen detecties.",
    "detect": lambda tekst, mem, std: ({}, []),
    "apply": lambda tekst, mapping: tekst,
}


def _to_markdown(pad):
    return _mock_state["to_markdown"](pad)


def _detect(tekst, mem, std):
    return _mock_state["detect"](tekst, mem, std)


def _apply(tekst, mapping):
    return _mock_state["apply"](tekst, mapping)


# Install mocks VOOR app.py wordt geimporteerd (module-load time, niet in fixture).
_install_mock_module("converter", to_markdown=_to_markdown)
_install_mock_module("detector", detect=_detect)
_install_mock_module("replacer", apply=_apply)


@pytest.fixture
def mock_anonimizer():
    """Geeft een handle om de mock-functies per test te overschrijven.

    Gebruik:
        def test_iets(mock_anonimizer):
            mock_anonimizer["detect"] = lambda t, m, s: ({}, [{"tekst": "Jan", ...}])
    """
    original = dict(_mock_state)
    yield _mock_state
    _mock_state.clear()
    _mock_state.update(original)


@pytest.fixture
def client(mock_anonimizer, tmp_path, monkeypatch):
    """Flask test-client met een verse session-store per test."""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-niet-voor-productie")
    # Forceer een per-test session dir zodat tests elkaar niet beinvloeden
    monkeypatch.setattr(
        "tempfile.gettempdir", lambda: str(tmp_path), raising=False
    )
    # app pas hier importeren: de mocks staan al in sys.modules
    import app as app_module
    import importlib
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
