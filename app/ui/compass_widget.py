"""
Compass Widget Component
"""

import math
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont


class CompassWidget(QWidget):
    """Compass widget showing cardinal directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.setStyleSheet("background-color: transparent;")

        # Layout for the compass
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        title = QLabel("COMPASS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            color: #d1d5db;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 4px;
        """
        )
        layout.addWidget(title)

        # Compass drawing area
        self.compass_area = CompassDrawingArea()
        layout.addWidget(self.compass_area)

    def set_direction(self, direction: str):
        """Set the current direction (N, S, E, W)."""
        self.compass_area.set_direction(direction)


class CompassDrawingArea(QWidget):
    """Custom widget for drawing the compass."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.direction = "N"  # Default direction
        self.setFixedSize(100, 100)

    def set_direction(self, direction: str):
        """Set the current direction."""
        self.direction = direction.upper()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center and radius
        center = self.rect().center()
        radius = min(self.width(), self.height()) / 2 - 5

        # Draw compass circle
        painter.setPen(QPen(QColor("#4b5563"), 2))
        painter.setBrush(QBrush(QColor("#1e1e1e")))
        painter.drawEllipse(center, radius, radius)

        # Draw cardinal direction markers
        painter.setPen(QPen(QColor("#9ca3af"), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        directions = {
            "N": (0, -radius + 15),
            "S": (0, radius - 15),
            "E": (radius - 15, 0),
            "W": (-radius + 15, 0),
        }

        for dir_name, (dx, dy) in directions.items():
            x = center.x() + dx
            y = center.y() + dy

            # Draw direction label
            painter.drawText(
                QRectF(x - 10, y - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, dir_name
            )

        # Draw needle pointing to current direction
        painter.setPen(QPen(QColor("#60a5fa"), 3))
        painter.setBrush(QBrush(QColor("#60a5fa")))

        # Calculate angle based on direction
        angles = {"N": 0, "E": 90, "S": 180, "W": 270}
        angle = angles.get(self.direction, 0)

        # Convert to radians
        rad_angle = math.radians(angle - 90)  # -90 to make N point up

        # Draw needle
        needle_length = radius - 10
        end_x = center.x() + needle_length * math.cos(rad_angle)
        end_y = center.y() + needle_length * math.sin(rad_angle)

        painter.drawLine(center.x(), center.y(), end_x, end_y)

        # Draw needle tip
        painter.drawEllipse(QRectF(end_x - 3, end_y - 3, 6, 6))
