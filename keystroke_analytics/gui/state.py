"""
GUI state machine for Keystroke Analytics.

Pure state logic: no side effects, no GUI widgets, no engine control.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class GuiState(Enum):
    IDLE = auto()
    CONSENT_PENDING = auto()
    RECORDING = auto()
    ERROR = auto()


class InvalidStateTransition(RuntimeError):
    """Raised when an invalid GUI state transition is attempted."""


@dataclass(frozen=True)
class GuiStateMachine:
    state: GuiState = GuiState.IDLE

    def transition(self, new_state: GuiState) -> "GuiStateMachine":
        allowed = {
            GuiState.IDLE: {GuiState.CONSENT_PENDING, GuiState.ERROR},
            GuiState.CONSENT_PENDING: {GuiState.RECORDING, GuiState.IDLE, GuiState.ERROR},
            GuiState.RECORDING: {GuiState.IDLE, GuiState.ERROR},
            GuiState.ERROR: {GuiState.IDLE},
        }

        if new_state not in allowed[self.state]:
            raise InvalidStateTransition(
                f"Invalid transition: {self.state.name} -> {new_state.name}"
            )
        return GuiStateMachine(state=new_state)