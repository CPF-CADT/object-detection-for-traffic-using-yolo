import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from app.utils.ui_helpers import COLORS


class CompassDrawingArea(QWidget):
    """Custom widget for drawing the compass without the "clock" lines."""

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
        
        # Configuration
        cam_map = {"N": "1", "S": "2", "E": "3", "W": "4"}
        angles = {"N": 270, "E": 0, "S": 90, "W": 180}
        
        # Distances from center
        text_radius = 55
        letter_radius = 28

        for dir_name, angle in angles.items():
            rad = math.radians(angle)

            # 1. Draw Camera Number (e.g., C1, C2...) furthest out
            cam_num = cam_map[dir_name]
            is_active = (dir_name == self.direction)
            
            tx = center.x() + text_radius * math.cos(rad)
            ty = center.y() + text_radius * math.sin(rad)
            
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            if is_active:
                painter.setPen(QPen(QColor("#3b82f6"), 2))
            else:
                painter.setPen(QPen(QColor("#3b82f6"), 1))
                
            painter.drawText(
                QRectF(tx - 20, ty - 15, 40, 30),
                Qt.AlignmentFlag.AlignCenter,
                f"C{cam_num}"
            )

            # 2. Draw Direction Letters (N, S, E, W) inside
            ix = center.x() + letter_radius * math.cos(rad)
            iy = center.y() + letter_radius * math.sin(rad)
            
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            if is_active:
                painter.setPen(QPen(QColor("#ffffff"), 1))
            else:
                painter.setPen(QPen(QColor("#6b7280"), 1))
                
            painter.drawText(
                QRectF(ix - 15, iy - 15, 30, 30),
                Qt.AlignmentFlag.AlignCenter,
                dir_name
            )

        # 3. Draw a subtle circular border around letters (Not a clock line)
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, letter_radius + 12, letter_radius + 12)

        # 4. Success highlight for active direction
        rad_active = math.radians(angles[self.direction])
        gx = center.x() + (letter_radius + 12) * math.cos(rad_active)
        gy = center.y() + (letter_radius + 12) * math.sin(rad_active)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#22c55e"))) # Success Green
        painter.drawEllipse(QRectF(gx - 4, gy - 4, 8, 8))
