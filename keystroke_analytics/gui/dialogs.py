"""
GUI dialogs for consent and passphrase input.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class ConsentDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Consent Required")
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "This tool captures keystrokes. Use only with explicit authorization.\n"
                "By continuing, you confirm you have consent to monitor this device."
            )
        )
        self._check = QCheckBox("I understand and have authorization")
        layout.addWidget(self._check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accepted_with_consent(self) -> bool:
        return self._check.isChecked()


class PassphraseDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Encryption Passphrase")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter passphrase (not saved):"))
        self._input = QLineEdit()
        self._input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self._input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def passphrase(self) -> str:
        return self._input.text().strip()