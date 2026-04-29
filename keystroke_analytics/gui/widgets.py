"""
Reusable custom widgets for consistent, polished UI components.
"""

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QFont, QLinearGradient, QColor, QPixmap, QIcon
from PySide6.QtWidgets import (
    QPushButton, 
    QLabel, 
    QFrame, 
    QVBoxLayout, 
    QHBoxLayout,
    QProgressBar,
    QWidget,
)
from .theme import Theme

class CustomButton(QPushButton):
    """Modern, animated button with hover effects."""
    
    def __init__(self, text="", icon="", role="primary"):
        super().__init__(text)
        self.setRole(role)
        self.setMinimumHeight(40)
        self._scale_anim = QPropertyAnimation(self, b"geometry")
        self._scale_anim.setDuration(150)
        self._scale_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    def setRole(self, role):
        """Set button role: primary, secondary, danger."""
        self._role = role
        self.setProperty("role", role)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def enterEvent(self, event):
        rect = self.geometry()
        self._scale_anim.setStartValue(QRect(rect))
        scaled_rect = rect.adjusted(-2, -2, 2, 2)
        self._scale_anim.setEndValue(QRect(scaled_rect))
        self._scale_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        rect = self.geometry()
        self._scale_anim.setStartValue(QRect(rect))
        self._scale_anim.setEndValue(QRect(rect.adjusted(2, 2, -2, -2)))
        self._scale_anim.start()
        super().leaveEvent(event)

class MetricCard(QFrame):
    """Dashboard-style metric card with icon, value, subtitle."""
    
    def __init__(self, icon="", value="0", subtitle="", accent_color="#00d4aa"):
        super().__init__()
        self.setProperty("role", "card")
        self._value = value
        self._accent_color = accent_color
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        
        # Icon row
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        self._icon_label = QLabel(icon)
        self._icon_label.setProperty("role", "subtitle")
        self._icon_label.setStyleSheet(f"color: {accent_color}; font-size: 24px;")
        icon_layout.addWidget(self._icon_label)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)
        
        # Value
        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setStyleSheet("font-size: 28px; font-weight: 700; margin: 0;")
        layout.addWidget(self._value_label)
        
        # Subtitle
        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setAlignment(Qt.AlignCenter)
        self._subtitle_label.setProperty("role", "subtitle")
        layout.addWidget(self._subtitle_label)
        
        layout.addStretch()
    
    def setValue(self, value):
        self._value_label.setText(str(value))
    
    def setAccent(self, color):
        self._accent_color = color
        self._icon_label.setStyleSheet(f"color: {color}; font-size: 24px;")

class StatusBadge(QLabel):
    """Animated status indicator badge."""
    
    STATES = {
        'idle': {'text': '🟠 Idle', 'color': '#ffa726'},
        'recording': {'text': '🟢 Recording', 'color': '#00d4aa'},
        'error': {'text': '🔴 Error', 'color': '#ff4757'},
        'paused': {'text': '🟡 Paused', 'color': '#ffb300'},
    }
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(32)
        self.setProperty("role", "status-idle")
        self.setText(self.STATES['idle']['text'])
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("padding: 8px 16px; border-radius: 16px; font-weight: 600;")
    
    def setStatus(self, state):
        """Set status: idle, recording, error, paused."""
        if state in self.STATES:
            config = self.STATES[state]
            self.setText(config['text'])
            self.setProperty("role", f"status-{state}")
            self.setStyleSheet(f"""
                QLabel[role="status-{state}"] {{
                    background: rgba({config['color']}, 0.15);
                    color: {config['color']};
                    padding: 8px 16px;
                    border-radius: 16px;
                    font-weight: 600;
                }}
            """)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

class ShadowFrame(QFrame):
    """Frame with customizable drop shadow."""
    
    def __init__(self, shadow_intensity="medium"):
        super().__init__()
        self._shadow_intensity = shadow_intensity
        self.setProperty("role", "shadow-frame")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#253044"))
        gradient.setColorAt(1, QColor("#1e2329"))
        painter.fillRect(self.rect(), gradient)
        
        # Shadow simulation
        shadow_offset = 4 if self._shadow_intensity == "strong" else 2
        shadow_rect = self.rect().adjusted(shadow_offset, shadow_offset, -shadow_offset, -shadow_offset)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 30))
        
        super().paintEvent(event)

class CircularProgress(QProgressBar):
    """Custom circular progress indicator."""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(60, 60)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border-radius: 30px;
                background-color: rgba(40, 45, 53, 0.5);
                border: 3px solid transparent;
            }
            QProgressBar::chunk {
                border-radius: 30px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00d4aa, stop:1 #00b894);
            }
        """)
    
    def paintEvent(self, event):
        # Custom circular painting can be added here
        super().paintEvent(event)

# Icon utilities (Unicode mapping for common icons)
ICONS = {
    'start': '▶️',
    'stop': '⏹️',
    'folder': '📁',
    'stats': '📊',
    'report': '📋',
    'logs': '📄',
    'key': '⌨️',
    'time': '⏱️',
    'speed': '⚡',
    'rhythm': '🎵',
    'warning': '⚠️',
    'shield': '🛡️',
}
