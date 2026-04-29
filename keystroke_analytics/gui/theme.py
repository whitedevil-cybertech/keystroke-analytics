"""
Centralized theme system for professional dark cybersecurity aesthetic.
"""

from PySide6.QtGui import QFont
from typing import Dict

class Theme:
    """Professional dark cybersecurity theme for the keystroke analytics GUI."""
    
    # Color Palette (Cybersecurity Dark)
    COLORS = {
        'bg_primary': '#0f1419',      # Deep navy background
        'bg_secondary': '#1a1f26',    # Darker panel bg
        'bg_card': '#1e2329',         # Card/panel containers
        'bg_hover': '#253044',        # Hover states
        'bg_accent': '#00d4aa',       # Teal success/accent
        'bg_warning': '#ff6b6b',      # Red error/warning
        'bg_info': '#2ed573',         # Green info
        'text_primary': '#e0e6ed',    # Light text
        'text_secondary': '#a0a8b0',  # Subtle text
        'text_muted': '#6b7280',      # Muted/placeholders
        'border': '#2a3443',          # Borders/dividers
        'border_hover': '#3a4453',    # Hover borders
        'shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.15)',
    }
    
    # Typography
    FONTS = {
        'title': "'Segoe UI', 'Inter', system-ui, sans-serif",
        'body': "'Segoe UI', system-ui, sans-serif",
        'mono': "'JetBrains Mono', 'Cascadia Code', 'Courier New', monospace",
    }
    
    # Sizing (rem-based, 16px root)
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
    }
    
    @classmethod
    def stylesheet(cls) -> str:
        """Complete QSS stylesheet for global application."""
        return f"""
        /* Global Reset & Base */
        * {{
            font-family: {cls.FONTS['body']};
            font-size: 13px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QMainWindow, QWidget {{
            background-color: {cls.COLORS['bg_primary']};
            border: none;
        }}
        
        /* Typography Hierarchy */
        QMainWindow::title {{
            font-weight: 700;
            font-size: 16px;
        }}
        
        QLabel {{
            color: {cls.COLORS['text_primary']};
        }}
        
        QLabel[role="title"] {{
            font-weight: 600;
            font-size: 16px;
            margin-bottom: {cls.SPACING['md']};
        }}
        
        QLabel[role="subtitle"] {{
            font-weight: 500;
            font-size: 14px;
            color: {cls.COLORS['text_secondary']};
        }}
        
        /* Cards & Panels */
        QFrame[role="card"], QGroupBox {{
            background-color: {cls.COLORS['bg_card']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: {cls.SPACING['lg']};
            margin: {cls.SPACING['sm']};
            box-shadow: {cls.COLORS['shadow']};
        }}
        
        QGroupBox::title {{
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            padding: 0 {cls.SPACING['md']};
            subcontrol-origin: margin;
        }}
        
        /* Buttons - Primary Brand */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {cls.COLORS['bg_accent']}, 
                stop:0.5 #00c9a3,
                stop:1 #00a085);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
            min-height: 32px;
            box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
            transition: all 0.2s ease;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00e6c0, 
                stop:0.5 #00d4aa,
                stop:1 {cls.COLORS['bg_accent']});
            box-shadow: 0 6px 20px rgba(0, 212, 170, 0.5);
            padding: 8px 16px;
            transform: translateY(-2px);
        }}
        
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00a085, 
                stop:0.5 #008f72,
                stop:1 #007a60);
            box-shadow: 0 2px 8px rgba(0, 212, 170, 0.3);
            transform: translateY(0);
        }}
        
        QPushButton:disabled {{
            background: {cls.COLORS['border']};
            color: {cls.COLORS['text_muted']};
            box-shadow: none;
        }}
        
        /* Secondary Buttons */
        QPushButton[role="secondary"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(42, 52, 67, 0.8),
                stop:1 rgba(37, 48, 68, 0.8));
            color: {cls.COLORS['text_primary']};
            border: 1.5px solid {cls.COLORS['border_hover']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 13px;
            min-height: 32px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
        }}
        
        QPushButton[role="secondary"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(52, 62, 77, 0.9),
                stop:1 rgba(47, 58, 78, 0.9));
            border-color: {cls.COLORS['bg_accent']};
            box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
            transform: translateY(-2px);
        }}
        
        QPushButton[role="secondary"]:pressed {{
            background: rgba(32, 42, 57, 0.8);
            transform: translateY(0);
        }}
        
        /* Danger Button */
        QPushButton[role="danger"] {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {cls.COLORS['bg_warning']},
                stop:0.5 #ff5252,
                stop:1 #ff3333);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
            min-height: 32px;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            transition: all 0.2s ease;
        }}
        
        QPushButton[role="danger"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #ff7f7f,
                stop:0.5 #ff6b6b,
                stop:1 {cls.COLORS['bg_warning']});
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
            transform: translateY(-2px);
        }}
        
        QPushButton[role="danger"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #ff3333,
                stop:0.5 #ff1f1f,
                stop:1 #dd0000);
            box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
            transform: translateY(0);
        }}
        
        QPushButton[role="danger"]:disabled {{
            background: {cls.COLORS['border']};
            color: {cls.COLORS['text_muted']};
            box-shadow: none;
        }}
        
        /* Status & Badges */
        QLabel[role="status-idle"] {{
            color: {cls.COLORS['text_secondary']};
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(107, 114, 128, 0.2);
        }}
        
        QLabel[role="status-recording"] {{
            color: {cls.COLORS['bg_accent']};
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(0, 212, 170, 0.15);
        }}
        
        QLabel[role="status-error"] {{
            color: {cls.COLORS['bg_warning']};
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(255, 107, 107, 0.15);
        }}
        
        /* Inputs */
        QLineEdit, QTextEdit {{
            background-color: {cls.COLORS['bg_secondary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 6px;
            padding: 10px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {cls.COLORS['bg_accent']};
            box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
        }}
        
        QLineEdit[readonly="true"], QTextEdit[readonly="true"] {{
            background-color: {cls.COLORS['bg_card']};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            color: {cls.COLORS['text_primary']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {cls.COLORS['border']};
            background-color: {cls.COLORS['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['bg_accent']};
            border: 2px solid {cls.COLORS['bg_accent']};
            image: none;
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {cls.COLORS['border_hover']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border']};
            background-color: {cls.COLORS['bg_secondary']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            padding: 12px 24px;
            margin-right: 4px;
            color: {cls.COLORS['text_secondary']};
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['bg_card']};
            color: {cls.COLORS['text_primary']};
            border-bottom: 3px solid {cls.COLORS['bg_accent']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {cls.COLORS['bg_hover']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background: {cls.COLORS['bg_secondary']};
            width: 12px;
            border-radius: 6px;
            margin: 0 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {cls.COLORS['text_muted']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {cls.COLORS['text_primary']};
        }}
        
        /* GroupBox */
        QGroupBox {{
            font-weight: 600;
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 12px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Dialogs */
        QDialog {{
            background-color: {cls.COLORS['bg_primary']};
        }}
        
        /* Progress Bars (for metrics) */
        QProgressBar {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 6px;
            text-align: center;
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {cls.COLORS['bg_accent']}, stop:1 rgba(0,212,170,0.8));
            border-radius: 4px;
        }}
        """
    
    @classmethod
    def font(cls, role: str) -> QFont:
        """Get themed font."""
        font = QFont()
        font_family = cls.FONTS.get(role, cls.FONTS['body'])
        # Qt doesn't parse CSS font-family strings directly, so approximate
        font.setFamily("Segoe UI")
        if role == 'mono':
            font.setFamily("Courier New")
        return font
