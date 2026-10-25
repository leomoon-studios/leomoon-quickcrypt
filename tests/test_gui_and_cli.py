from __future__ import annotations

import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui


def test_browse_drag_drop_and_clear_actions(quickcrypt_window, monkeypatch, tmp_path) -> None:
    source = tmp_path / "نمونه file.txt"
    source.write_text("QuickCrypt GUI test", encoding="utf-8")

    from main import QtWidgets

    monkeypatch.setattr(
        QtWidgets.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(source), ""),
    )
    quickcrypt_window._encBrowse()
    assert quickcrypt_window.ui.encFileInp.text() == str(source)

    mime_data = QtCore.QMimeData()
    mime_data.setUrls([QtCore.QUrl.fromLocalFile(str(source))])
    event = QtGui.QDropEvent(
        QtCore.QPointF(0, 0), QtCore.Qt.CopyAction, mime_data, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier
    )
    quickcrypt_window.dropEvent(event)
    assert quickcrypt_window.ui.encFileInp.text() == str(source)
    assert quickcrypt_window.ui.decFileInp.text() == str(source)

    quickcrypt_window.ui.encPassInp.setText("password")
    quickcrypt_window.ui.historyEdit.setPlainText("generated")
    quickcrypt_window._clearall()
    assert not quickcrypt_window.ui.encFileInp.text()
    assert not quickcrypt_window.ui.encPassInp.text()
    assert not quickcrypt_window.ui.historyEdit.toPlainText()
    assert quickcrypt_window.ui.statusLbl.text() == "All fields cleared."


def test_theme_password_confirmation_and_status(quickcrypt_window, tmp_path) -> None:
    source = tmp_path / "input.txt"
    source.write_text("QuickCrypt GUI test", encoding="utf-8")

    initial_theme = quickcrypt_window.themeFlg
    quickcrypt_window._theme()
    assert quickcrypt_window.themeFlg is not initial_theme

    quickcrypt_window.ui.encFileInp.setText(str(source))
    quickcrypt_window.ui.encPassInp.setText("one")
    quickcrypt_window.ui.encPassConfirmInp.setText("two")
    quickcrypt_window._encrypt()
    assert "Passwords do not match" in quickcrypt_window.ui.statusLbl.text()
    assert not (tmp_path / "input.txt.aes").exists()


def test_password_generator_status_and_output(quickcrypt_window) -> None:
    quickcrypt_window.ui.lengthSbox.setValue(48)
    quickcrypt_window.ui.pppCbox.setChecked(True)
    quickcrypt_window._passgen()

    password = quickcrypt_window.ui.historyEdit.toPlainText().splitlines()[-1]
    assert len(password) == 48
    assert "successfully" in quickcrypt_window.ui.statusLbl.text()


def test_cli_encrypt_and_decrypt_modes_accept_space_and_unicode_paths(qtbot, monkeypatch, tmp_path) -> None:
    import main

    source = tmp_path / "نمونه input.txt"
    encrypted = tmp_path / "نمونه input.txt.aes"
    source.write_text("QuickCrypt CLI test", encoding="utf-8")
    encrypted.write_bytes(b"AES")

    monkeypatch.setattr(sys, "argv", ["QuickCrypt", "-e", str(source)])
    encrypt_window = main.mainUi()
    qtbot.addWidget(encrypt_window)
    assert encrypt_window.ui.encFileInp.text() == str(source)
    assert not encrypt_window.ui.tabWidget.isTabEnabled(1)

    monkeypatch.setattr(sys, "argv", ["QuickCrypt", "-d", str(encrypted)])
    decrypt_window = main.mainUi()
    qtbot.addWidget(decrypt_window)
    assert decrypt_window.ui.decFileInp.text() == str(encrypted)
    assert not decrypt_window.ui.tabWidget.isTabEnabled(0)
    assert not decrypt_window.ui.tabWidget.isTabEnabled(2)


def test_legacy_windows_shell_commands_preserve_cli_mode_and_file_argument() -> None:
    installer = (
        Path(__file__).resolve().parents[1] / "src" / "_setup" / "setupgen.iss"
    ).read_text(encoding="utf-8")

    assert '""{app}\\{#AppExeName}"" -e ""%1""' in installer
    assert '""{app}\\{#AppExeName}"" -d ""%1""' in installer
