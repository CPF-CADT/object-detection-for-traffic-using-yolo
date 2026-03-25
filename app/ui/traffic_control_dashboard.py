"""
Traffic Control Dashboard Component (Modularized)
"""

import os
import qtawesome as qta
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)
from PySide6.QtCore import Qt
from .camera_widget_yolo import CameraWidget
from .compass_widget import CompassWidget
from .review_sidebar import ReviewSidebar
from app.config import VIDEO_STORAGE_DIR
from app.global_controller import GlobalTrafficController
from app.utils.ui_helpers import COLORS, STYLES, create_hbox_layout, create_vbox_layout


class TrafficControlDashboard(QMainWindow):
    """Main window: header + 2×2 camera grid + status bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Control System")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 800)

        # Global dark background
        self.setStyleSheet(f"QMainWindow {{ background-color: {COLORS['bg-dark']}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = create_vbox_layout()
        central.setLayout(main_layout)

        # ── Header ──
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(STYLES["header"])
        header_layout = create_hbox_layout(margins=(24, 0, 24, 0))
        header.setLayout(header_layout)

        title = QLabel("TRAFFIC CONTROL SYSTEM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"color: {COLORS['text-bright']}; font-size: 20px; font-weight: 700; letter-spacing: 2px;"
        )

        # Main Start Button
        self.start_button = QPushButton("START SIMULATION")
        self.start_button.setFixedSize(160, 36)
        self.start_button.setStyleSheet(STYLES["button-success"])
        self.start_button.clicked.connect(self._start_simulation)

        # Main Stop Button
        self.stop_button = QPushButton("TERMINATE")
        self.stop_button.setFixedSize(140, 36)
        self.stop_button.setStyleSheet(STYLES["button-danger"])
        self.stop_button.clicked.connect(self.close)

        header_layout.addWidget(title, stretch=1)
        header_layout.addWidget(self.start_button)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.stop_button)
        main_layout.addWidget(header)

        # ── Main Content Area ──
        content_area = QWidget()
        content_layout = create_hbox_layout()
        content_area.setLayout(content_layout)

        # Left Sidebar
        self.review_sidebar = ReviewSidebar()
        content_layout.addWidget(self.review_sidebar)

        # Center - Camera Grid
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(16)

        self.camera_widgets = []
        for i in range(4):
            cam = CameraWidget(camera_id=i + 1)
            grid_layout.addWidget(cam, i // 2, i % 2)
            self.camera_widgets.append(cam)

        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        content_layout.addWidget(grid_container, stretch=1)

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        content_layout.addWidget(grid_container, stretch=1)

        # Global Controller for traffic flow
        self.traffic_controller = GlobalTrafficController(self.camera_widgets, self)

        # Right Sidebar - Compass and Controls
        right_sidebar = QWidget()
        right_sidebar.setFixedWidth(200)
        right_sidebar.setStyleSheet(
            "background-color: #1a1a1a; border-left: 1px solid #333333;"
        )
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(16)

        # Compass Section
        compass_section = QWidget()
        compass_layout = QVBoxLayout(compass_section)
        compass_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        compass_title = QLabel("NAVIGATION")
        compass_title.setStyleSheet(
            """
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 8px;
        """
        )
        compass_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.compass = CompassWidget()
        self.compass.set_direction("N")

        compass_layout.addWidget(compass_title)
        compass_layout.addWidget(self.compass)
        compass_layout.addStretch()

        right_layout.addWidget(compass_section)

        # Camera Direction Controls
        direction_section = QWidget()
        direction_layout = QVBoxLayout(direction_section)

        direction_title = QLabel("CAMERA DIRECTIONS")
        direction_title.setStyleSheet(
            """
            color: #9ca3af;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        """
        )
        direction_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        direction_layout.addWidget(direction_title)

        self.direction_buttons = {}
        directions = [("North", "N"), ("South", "S"), ("East", "E"), ("West", "W")]
        for idx, (name, code) in enumerate(directions):
            cam_num = idx + 1
            btn = QLabel(f"{name} ({code}) - Cam {cam_num}")
            btn.setStyleSheet(
                """
                QLabel {
                    background-color: #2a2a2a;
                    color: #d1d5db;
                    padding: 6px 12px;
                    border-radius: 4px;
                    border: 1px solid #444444;
                    margin: 2px 0;
                }
                QLabel:hover {
                    background-color: #3a3a3a;
                }
                """
            )
            btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn.mousePressEvent = lambda e, d=code: self._set_camera_direction(d)
            direction_layout.addWidget(btn)
            self.direction_buttons[code] = btn

        right_layout.addWidget(direction_section)
        right_layout.addStretch()

        content_layout.addWidget(right_sidebar)

        main_layout.addWidget(content_area, stretch=1)

        # ── Footer / Status Bar ──
        footer = QWidget()
        footer.setFixedHeight(44)
        footer.setStyleSheet(
            """
            background-color: #1e1e1e;
            border-top: 1px solid #333333;
        """
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.setSpacing(16)

        # Status
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")
        status_value = QLabel("System Active")
        status_value.setStyleSheet("color: #4ade80; font-size: 13px; font-weight: 500;")

        # Separator
        sep1 = QFrame()
        sep1.setFixedSize(1, 16)
        sep1.setStyleSheet("background-color: #333333;")

        # Mode
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        mode_value = QLabel("Manual")
        mode_value.setStyleSheet("color: #60a5fa; font-size: 13px; font-weight: 500;")

        # Separator
        sep2 = QFrame()
        sep2.setFixedSize(1, 16)
        sep2.setStyleSheet("background-color: #333333;")

        # Time Sync
        sync_label = QLabel("Time Sync:")
        sync_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        sync_value = QLabel("OK")
        sync_value.setStyleSheet("color: #4ade80; font-size: 13px; font-weight: 500;")

        for w in (
            status_label,
            status_dot,
            status_value,
            sep1,
            mode_label,
            mode_value,
            sep2,
            sync_label,
            sync_value,
        ):
            footer_layout.addWidget(w)

        main_layout.addWidget(footer)

    def _set_camera_direction(self, direction: str):
        """Update the compass and status to reflect the selected camera's perspective."""
        print(f"DEBUG: Setting view direction to: {direction}")
        self.compass.set_direction(direction)

        # Update UI feedback on buttons
        for code, btn in self.direction_buttons.items():
            if code == direction:
                btn.setStyleSheet(
                    """
                    QLabel {
                        background-color: #3b82f6;
                        color: #ffffff;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: 1px solid #60a5fa;
                        margin: 2px 0;
                        font-weight: bold;
                    }
                    """
                )
            else:
                btn.setStyleSheet(
                    """
                    QLabel {
                        background-color: #2a2a2a;
                        color: #d1d5db;
                        padding: 6px 12px;
                        border-radius: 4px;
                        border: 1px solid #444444;
                        margin: 2px 0;
                    }
                    QLabel:hover {
                        background-color: #3a3a3a;
                    }
                    """
                )

        # Update status bar mode/direction info
        for child in self.findChildren(QLabel):
            if child.text() == "Manual" or "View:" in child.text():
                child.setText(f"View: {direction}")
                child.setStyleSheet(
                    "color: #60a5fa; font-size: 13px; font-weight: 500;"
                )
                break

    def _start_simulation(self):
        """Start the traffic simulation."""
        print("Starting traffic simulation...")
        self.start_button.setText("STOP SIMULATION")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
            """
        )
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self._stop_simulation)

        # Start all camera workers (inference starts)
        for camera in self.camera_widgets:
            camera.start_simulation()
            # Ensure all start as RED initially
            camera.set_light("RED")

        # Start global traffic flow (lights management)
        self.traffic_controller.start()

        # Explicitly force Camera 1 to GREEN to start the sequence
        if len(self.camera_widgets) > 0:
            print("Forcing Camera 1 to GREEN for initial cycle...")
            self.camera_widgets[0].set_light("GREEN")

        # Ensure the first camera (C1) is actually resumed
        # because load_video initially started them all in PAUSED mode
        if len(self.camera_widgets) > 0:
            self.camera_widgets[0].set_light(
                "GREEN"
            )  # Triggers worker.resume() via _on_light_clicked

    def _stop_simulation(self):
        """Stop the traffic simulation."""
        print("Stopping traffic simulation...")
        self.start_button.setText("START SIMULATION")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4ade80;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #22c55e;
            }
            QPushButton:pressed {
                background-color: #16a34a;
            }
            """
        )
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self._start_simulation)

        # Stop global flow first
        self.traffic_controller.stop()

        # Stop all camera videos
        for camera in self.camera_widgets:
            camera.stop_simulation()

    def _set_camera_direction(self, direction):
        """Set the compass direction."""
        self.compass.set_direction(direction)

    def _load_video_to_camera(self, camera_widget, video_name):
        """Load a video into a camera widget."""
        # This method is now handled by the camera widget's drop event
        pass
