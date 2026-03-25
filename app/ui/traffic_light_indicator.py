"""
Traffic Light Indicator Component
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QBrush


class TrafficLightIndicator(QPushButton):
    """Clickable traffic-light circle with active glow effect."""

    COLORS = {
        "red": {
            "active": "#dc2626",
            "inactive": "#450a0a",
            "glow": "rgba(220,38,38,0.8)",
        },
        "yellow": {
            "active": "#facc15",
            "inactive": "#422006",
            "glow": "rgba(250,204,21,0.8)",
        },
        "green": {
            "active": "#22c55e",
            "inactive": "#052e16",
            "glow": "rgba(34,197,94,0.8)",
        },
    }

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._active = False
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{color.capitalize()} Light")
        self._apply_style()

    @property
    def color(self) -> str:
        return self._color

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def _apply_style(self):
        palette = self.COLORS[self._color]
        if self._active:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {palette['active']};
                    border: 2px solid #4b5563;
                    border-radius: 14px;
                    min-width: 28px; min-height: 28px;
                    max-width: 28px; max-height: 28px;
                }}
            """
            )
        else:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {palette['inactive']};
                    border: 2px solid #1f2937;
                    border-radius: 14px;
                    min-width: 28px; min-height: 28px;
                    max-width: 28px; max-height: 28px;
                }}
            """
            )

    # Paint a glow halo behind the button when active
    def paintEvent(self, event):
        if self._active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            center = self.rect().center()
            palette = self.COLORS[self._color]
            grad = QRadialGradient(center, 18)
            base = QColor(palette["active"])
            base.setAlpha(100)
            grad.setColorAt(0, base)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, 18, 18)
            painter.end()
        super().paintEvent(event)
