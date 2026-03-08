"""
VS Code-style notification system for TagQt.

Notifications appear bottom-center with colored left border,
icon, title, and optional close button. Matches Catppuccin Mocha styling.
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect, QPushButton, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QEvent, QPoint
)
from tagqt.ui.theme import Theme


class ToastType:
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


def _get_type_config(toast_type):
    """Resolve colors at call time so theme switches take effect."""
    configs = {
        ToastType.INFO:    (Theme.BLUE,  "ℹ",  4000),
        ToastType.SUCCESS: (Theme.GREEN, "✓",  4000),
        ToastType.WARNING: (Theme.PEACH, "⚠", 6000),
        ToastType.ERROR:   (Theme.RED,   "✕",  0),
    }
    return configs.get(toast_type, configs[ToastType.INFO])


class ToastWidget(QWidget):
    """A single VS Code-style notification widget."""

    def __init__(self, message, parent=None, duration=None, toast_type=ToastType.INFO):
        super().__init__(parent)
        self.raise_()
        self.setFixedWidth(320)

        accent, icon_char, auto_ms = _get_type_config(toast_type)
        if duration is None:
            duration = auto_ms

        # Main container layout
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Left accent border (3px solid color)
        accent_bar = QWidget()
        accent_bar.setFixedWidth(3)
        accent_bar.setStyleSheet(f"background-color: {accent}; border-radius: 0px;")
        outer.addWidget(accent_bar)

        # Body
        body = QWidget()
        body.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SURFACE0};
                border: 1px solid {Theme.SURFACE1};
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
        """)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        # Icon
        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(16, 16)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        body_layout.addWidget(icon_label, 0, Qt.AlignTop)

        # Text
        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
        body_layout.addWidget(text_label, 1)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(18, 18)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {Theme.OVERLAY1};
                background: transparent;
                border: none;
                font-size: 12px;
                padding: 0px;
                min-height: 0px;
            }}
            QPushButton:hover {{
                color: {Theme.TEXT};
            }}
        """)
        close_btn.clicked.connect(self.start_fade_out)
        body_layout.addWidget(close_btn, 0, Qt.AlignTop)

        outer.addWidget(body)

        self.adjustSize()

        # Opacity effect for fade animations
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Fade in (150ms)
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(150)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)

        # Fade out (200ms)
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InQuad)
        self.fade_out.finished.connect(self.close)

        # Auto-dismiss timer
        self.timer = None
        if duration > 0:
            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.start_fade_out)
            self.timer.start(duration)

        self.fade_in.start()

    def stop_timer(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()

    def start_fade_out(self):
        self.stop_timer()
        if self.fade_in.state() == QPropertyAnimation.Running:
            self.fade_in.stop()
            current_opacity = self.opacity_effect.opacity()
            self.fade_out.setStartValue(current_opacity)
        self.fade_out.start()

    def mousePressEvent(self, event):
        self.start_fade_out()


class ToastManager(QWidget):
    """Manages VS Code-style notification stacking in bottom-right corner."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 16)
        self.layout.setSpacing(8)

        self.current_toast = None

        if parent:
            self.resize(parent.size())
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            self.resize(event.size())
        return super().eventFilter(obj, event)

    def show_message(self, message, duration=None, toast_type=ToastType.INFO):
        if self.current_toast:
            try:
                self.current_toast.stop_timer()
                self.current_toast.close()
                self.current_toast.deleteLater()
            except RuntimeError:
                pass
            self.current_toast = None

        self._spawn_toast(message, duration, toast_type)

    def show_success(self, message, duration=None):
        self.show_message(message, duration, ToastType.SUCCESS)

    def show_error(self, message, duration=None):
        self.show_message(message, duration, ToastType.ERROR)

    def _spawn_toast(self, message, duration, toast_type):
        toast = ToastWidget(message, self.parent(), duration, toast_type)
        self.current_toast = toast
        toast.show()

        # Position: bottom-center with 16px bottom margin
        pw = self.parent().width()
        ph = self.parent().height()
        target_x = (pw - toast.width()) // 2
        target_y = ph - toast.height() - 16

        toast.move(target_x, target_y)
