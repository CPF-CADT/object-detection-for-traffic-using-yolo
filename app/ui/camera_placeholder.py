import qtawesome as qta
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from app.utils.ui_helpers import COLORS


class CameraPlaceholder(QFrame):
    """Visual placeholder when no video is loaded."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet(
            f"""
            border: 2px dashed {COLORS['text-dim']};
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.8);
        """
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon("fa5.play-circle", color="#6b7280").pixmap(48, 48)
        )
        icon_label.setStyleSheet("border: none; background: transparent;")

        drop_label = QLabel("Drop Video Here")
        drop_label.setStyleSheet(
            "color: #6b7280; font-size: 13px; border: none; background: transparent;"
        )

        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(drop_label, alignment=Qt.AlignmentFlag.AlignCenter)
