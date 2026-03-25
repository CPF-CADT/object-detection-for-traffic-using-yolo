from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from app.utils.ui_helpers import COLORS


class CardinalLabel(QLabel):
    """Simple label for cardinal direction."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"color: {COLORS['text-dim']}; font-weight: 600; font-size: 12px;"
        )
