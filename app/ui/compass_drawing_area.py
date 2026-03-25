import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from app.utils.ui_helpers import COLORS


class CompassDrawingArea(QWidget):
    """Custom widget for drawing the compass (Ring and Needle)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.direction = "N"
        self.setFixedSize(160, 160)

    def set_direction(self, direction: str):
        self.direction = direction.upper()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = 30

        # Draw circle
        painter.setPen(QPen(QColor(COLORS["border"]), 2))
        painter.setBrush(QBrush(QColor(COLORS["bg-surface"])))
        painter.drawEllipse(center, radius, radius)

        # Draw direction markers
        painter.setPen(QPen(QColor(COLORS["text-dim"]), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        directions = {
            "N": (0, -radius + 15, radius + 35),
            "S": (0, radius - 15, radius + 35),
            "E": (radius - 15, 0, radius + 35),
            "W": (-radius + 15, 0, radius + 35),
        }
        cam_map = {"N": "1", "S": "2", "E": "3", "W": "4"}

        for dir_name, (dx, dy, outer_r) in directions.items():
            x = center.x() + dx
            y = center.y() + dy
            painter.setPen(QPen(QColor(COLORS["text-dim"]), 1))
            painter.drawText(
                QRectF(x - 10, y - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, dir_name
            )

            # Camera number
            cam_num = cam_map[dir_name]
            angle_map = {"N": 270, "E": 0, "S": 90, "W": 180}
            rad = math.radians(angle_map[dir_name])
            ox = center.x() + outer_r * math.cos(rad)
            oy = center.y() + outer_r * math.sin(rad)

            painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(COLORS["primary"]), 1))
            painter.drawText(
                QRectF(ox - 15, oy - 15, 30, 30),
                Qt.AlignmentFlag.AlignCenter,
                f"C{cam_num}",
            )

        # Needle
        painter.setPen(QPen(QColor(COLORS["success"]), 4))
        painter.setBrush(QBrush(QColor(COLORS["success"])))
        angles = {"N": 0, "E": 90, "S": 180, "W": 270}
        angle = angles.get(self.direction, 0)
        rad_angle = math.radians(angle - 90)

        needle_length = radius - 10
        end_x = center.x() + needle_length * math.cos(rad_angle)
        end_y = center.y() + needle_length * math.sin(rad_angle)
        painter.drawLine(center.x(), center.y(), end_x, end_y)

        # Tip
        painter.setPen(QPen(QColor(COLORS["text-bright"]), 1))
        painter.setBrush(QBrush(QColor(COLORS["text-bright"])))
        painter.drawEllipse(QRectF(end_x - 3, end_y - 3, 6, 6))

        # Direction text Overlay
        painter.setPen(QPen(QColor(COLORS["text-bright"]), 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, f"\n\n\n{self.direction}"
        )
