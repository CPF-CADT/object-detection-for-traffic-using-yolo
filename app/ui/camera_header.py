import qtawesome as qta
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QPushButton
from PySide6.QtCore import Qt
from app.utils.ui_helpers import COLORS, STYLES, create_hbox_layout


class CameraHeader(QWidget):
    """Header component for CameraWidget with title, controls and status badges."""

    def __init__(self, camera_id, on_load, on_switch, on_timer_change, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLES["header"])
        layout = create_hbox_layout(margins=(12, 8, 12, 8), spacing=8)

        self.title_label = QLabel(f"Camera {camera_id}")
        self.title_label.setStyleSheet(STYLES["title"])

        # Buttons
        self.load_btn = self._create_icon_btn(
            "fa5s.folder-open", on_load, "Select video file"
        )
        self.switch_btn = self._create_icon_btn(
            "fa5s.exchange-alt", on_switch, "Load selected from sidebar"
        )

        # Timer Input
        self.timer_input = QSpinBox()
        self.timer_input.setRange(5, 120)
        self.timer_input.setSuffix("s Green")
        self.timer_input.valueChanged.connect(on_timer_change)
        self.timer_input.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: #2a2a2a; color: #ffffff;
                border: 1px solid {COLORS['border']}; border-radius: 4px;
                padding: 2px 4px; font-size: 11px; width: 70px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; }}
        """
        )

        # Status
        self.count_badge = QLabel("0 Vehicles")
        self.count_badge.setStyleSheet(
            f"""
            background-color: {COLORS['primary']}; color: {COLORS['text-bright']};
            border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold; border: none;
        """
        )

        self.timer_label = QLabel("0s")
        self.timer_label.setStyleSheet(
            "color: #ffffff; font-weight: 700; font-size: 20px; border: none;"
        )

        layout.addWidget(self.title_label)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.switch_btn)
        layout.addSpacing(4)
        layout.addWidget(self.timer_input)
        layout.addStretch()
        layout.addWidget(self.count_badge)
        layout.addSpacing(12)
        layout.addWidget(self.timer_label)
        self.setLayout(layout)

    def _create_icon_btn(self, icon_name, callback, tooltip):
        btn = QPushButton()
        btn.setIcon(qta.icon(icon_name, color=COLORS["text-dim"]))
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        btn.setStyleSheet(
            f"""
            QPushButton {{ background-color: transparent; border: 1px solid {COLORS['border']}; border-radius: 4px; }}
            QPushButton:hover {{ background-color: {COLORS['border']}; border-color: {COLORS['primary']}; }}
        """
        )
        return btn
