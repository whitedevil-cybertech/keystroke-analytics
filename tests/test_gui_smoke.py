"""
GUI smoke test using real Qt widgets and QTest interaction.

Security note:
- EngineController is stubbed to prevent real keystroke capture.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialogButtonBox,
    QPushButton,
)

from keystroke_analytics.gui import main_window as main_window_module
from keystroke_analytics.gui.dialogs import ConsentDialog


pytest.importorskip("PySide6")


class FakeEngineController(QObject):
    started = Signal()
    stopped = Signal()
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self, _overrides) -> None:
        self._running = True
        self.started.emit()

    def stop(self) -> None:
        self._running = False
        self.stopped.emit()


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _find_button(parent, text: str) -> QPushButton:
    for btn in parent.findChildren(QPushButton):
        if btn.text().strip() == text:
            return btn
    raise AssertionError(f"Button with text '{text}' not found.")


def test_gui_start_stop_with_consent(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure no real capture runs in tests.
    monkeypatch.setattr(main_window_module, "EngineController", FakeEngineController)

    window = main_window_module.MainWindow(
        config_path=None,
        log_dir=None,
        encrypt=False,  # avoid passphrase dialog in smoke test
        analytics_enabled=True,
    )
    window.show()
    QTest.qWaitForWindowExposed(window)

    start_btn = _find_button(window, "Start Capture")
    stop_btn = _find_button(window, "Stop Capture")

    assert window._status.text() == "Status: Idle"
    assert start_btn.isEnabled()
    assert not stop_btn.isEnabled()

    # Auto-handle the consent dialog after it appears.
    def _accept_consent() -> None:
        for widget in qapp.topLevelWidgets():
            if isinstance(widget, ConsentDialog):
                checkbox = widget.findChild(QCheckBox)
                assert checkbox is not None
                checkbox.setChecked(True)

                button_box = widget.findChild(QDialogButtonBox)
                assert button_box is not None
                ok_button = button_box.button(QDialogButtonBox.Ok)
                assert ok_button is not None

                QTest.mouseClick(ok_button, Qt.LeftButton)
                return

    QTimer.singleShot(0, _accept_consent)
    QTest.mouseClick(start_btn, Qt.LeftButton)
    QTest.qWait(100)

    assert window._status.text() == "Status: Recording"
    assert not start_btn.isEnabled()
    assert stop_btn.isEnabled()

    QTest.mouseClick(stop_btn, Qt.LeftButton)
    QTest.qWait(100)

    assert window._status.text() == "Status: Idle"
    assert start_btn.isEnabled()
    assert not stop_btn.isEnabled()

    window.close()