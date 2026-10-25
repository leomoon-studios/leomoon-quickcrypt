# Third-Party Notices

## Qt for Python and Qt 6

LeoMoon QuickCrypt uses PySide6 6.12.0 and Qt 6.12.0. The project selects the GPL-3.0-only option offered by the PySide6 packages, consistent with the project's GPL-3.0-only distribution model.

PySide6, PySide6-Essentials, PySide6-Addons, and Shiboken6 are copyright The Qt Company Ltd. and other contributors. Their package metadata identifies the available license expression as `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; this project distributes them under the GPL-3.0-only option.

Qt for Python licensing information is available at <https://doc.qt.io/qtforpython-6/licenses.html>.

## DarkDetect

LeoMoon QuickCrypt uses DarkDetect 0.8.0, copyright Alberto Sottile and contributors, from <https://github.com/albertosottile/darkdetect>. DarkDetect is licensed under the BSD 3-Clause License.

## pyAesCrypt and Cryptography

LeoMoon QuickCrypt uses pyAesCrypt 6.1.1 by Marco Bellaccini, from <https://github.com/marcobellaccini/pyAesCrypt>. pyAesCrypt is licensed under the Apache License 2.0 and implements the AES Crypt version 2 file format.

The project uses Cryptography 50.0.2 from the Python Cryptographic Authority and contributors. Cryptography is licensed under Apache-2.0 OR BSD-3-Clause.

AES Crypt version 2 does not authenticate its file-size-modulo-16 byte. An attacker who can modify an encrypted file can alter the recovered plaintext size by up to 15 bytes. Passwords cannot be reliably wiped from Python process memory.

## Vazir fonts

The bundled Vazir Regular and Vazir Black font faces are from the Vazir font family by Saber Rastikerdar, available at <https://github.com/rastikerdar/vazir-font>. Vazir is licensed under the SIL Open Font License 1.1.

## Application artwork

The bundled LeoMoon QuickCrypt application icon artwork is original LeoMoon Studios artwork and is not a third-party component.
