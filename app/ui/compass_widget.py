"""
Compass Widget Component (Modularized)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .cardinal_label import CardinalLabel
from .compass_drawing_area import CompassDrawingArea


class CompassWidget(QWidget):
    """Container for the compass component."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 200)
        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        self.title_label = CardinalLabel("COMPASS")
        layout.addWidget(self.title_label)

        self.compass_area = CompassDrawingArea()
        layout.addWidget(self.compass_area, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_direction(self, direction: str):
        self.compass_area.set_direction(direction)
