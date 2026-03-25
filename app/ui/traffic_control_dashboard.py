"""
Traffic Control Dashboard Component
"""

import os

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
from .camera_widget import CameraWidget
from .compass_widget import CompassWidget
from .review_sidebar import ReviewSidebar
from app.config import UI_SETTINGS


class TrafficControlDashboard(QMainWindow):
    """Main window: header + 2×2 camera grid + status bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Control System")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 800)

        # Global dark stylesheet
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121212;
            }
        """
        )

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(
            """
            background-color: #1e1e1e;
            border-bottom: 1px solid #333333;
        """
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)

        title = QLabel("TRAFFIC CONTROL SYSTEM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            color: #ffffff;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 2px;
        """
        )

        # Main Start Button
        self.start_button = QPushButton("START SIMULATION")
        self.start_button.setFixedSize(160, 36)
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
        self.start_button.clicked.connect(self._start_simulation)

        header_layout.addWidget(title, stretch=1)
        header_layout.addWidget(
            self.start_button, alignment=Qt.AlignmentFlag.AlignRight
        )
        main_layout.addWidget(header)

        # ── Main Content Area (Video Editor Style) ──
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left Sidebar - Review Area
        self.review_sidebar = ReviewSidebar()
        content_layout.addWidget(self.review_sidebar)

        # Center - Camera Grid
        grid_container = QWidget()
        grid_container.setStyleSheet("background: transparent;")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(16)

        self.camera_widgets = []
        for i in range(4):
            cam = CameraWidget(camera_id=i + 1)
            # Enable drop for camera widgets
            cam.setAcceptDrops(True)
            cam.dragEnterEvent = lambda e, c=cam: self._camera_drag_enter(e, c)
            cam.dropEvent = lambda e, c=cam: self._camera_drop(e, c)
            grid_layout.addWidget(cam, i // 2, i % 2)
            self.camera_widgets.append(cam)

        # Set equal row and column stretches for uniform video sizes
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        content_layout.addWidget(grid_container, stretch=1)

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
        for name, code in directions:
            btn = QLabel(f"{name} ({code})")
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

        # Start all camera videos
        for camera in self.camera_widgets:
            camera.start_simulation()

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

        # Stop all camera videos
        for camera in self.camera_widgets:
            camera.stop_simulation()

    # ── Event Handlers ──
    def _camera_drag_enter(self, event, camera_widget):
        """Handle drag enter for camera widgets."""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def _camera_drop(self, event, camera_widget):
        """Handle drop for camera widgets."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    camera_widget._load_video_file(file_path)
                    event.acceptProposedAction()
        elif event.mimeData().hasText():
            video_name = event.mimeData().text()
            # Try to find the video in default storage directory
            video_path = os.path.join(self.VIDEO_STORAGE_DIR, video_name)
            if os.path.exists(video_path):
                camera_widget._load_video_file(video_path)
                event.acceptProposedAction()

    def _set_camera_direction(self, direction):
        """Set the compass direction."""
        self.compass.set_direction(direction)

    def _load_video_to_camera(self, camera_widget, video_name):
        """Load a video into a camera widget."""
        # This method is now handled by the camera widget's drop event
        pass
