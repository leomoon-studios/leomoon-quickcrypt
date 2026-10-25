from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_ROOT))


@pytest.fixture
def quickcrypt_window(qtbot, monkeypatch):
    from leomoon_quickcrypt import app

    monkeypatch.setattr(sys, "argv", ["QuickCrypt"])
    window = app.mainUi()
    qtbot.addWidget(window)
    return window
