"""
Camera Widget Component
"""

from turtle import color

from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

from app.config import DEFAULT_VIDEOS, VIDEO_STORAGE_DIR
from .traffic_light_indicator import TrafficLightIndicator
import qtawesome as qta
import os


class CameraWidget(QFrame):
    """Reusable camera panel: title, timer, video placeholder, traffic lights."""

    TIMERS = {"red": 30, "yellow": 5, "green": 25}

    def __init__(self, camera_id: int, parent=None):
        super().__init__(parent)
        self._camera_id = camera_id
        self._active_light = "red"
        self._current_video = None
        self._traffic_density = 0  # 0 = default/no cars, 1-4 = traffic levels

        self.setStyleSheet(
            """
            CameraWidget {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setStyleSheet(
            "background-color: #1e1e1e; border-bottom: 1px solid #333333;"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel(f"Camera {camera_id}")
        title.setStyleSheet(
            "color: #d1d5db; font-weight: 600; font-size: 14px; border: none;"
        )

        self._timer_label = QLabel(f"{self.TIMERS[self._active_light]}s")
        self._timer_label.setStyleSheet(
            "color: #ffffff; font-weight: 700; font-size: 20px; border: none;"
        )
        self._timer_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self._timer_label)
        root.addWidget(header)

        # ── Video area with media player ──
        self._video_container = QWidget()
        self._video_container.setStyleSheet("background-color: #000000; border: none;")
        self._video_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        video_layout = QVBoxLayout(self._video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)

        # Video widget for playback
        self._video_widget = QVideoWidget()
        self._video_widget.setStyleSheet("background-color: #000000;")
        video_layout.addWidget(self._video_widget, stretch=1)

        # Media player
        self._media_player = QMediaPlayer()
        self._media_player.setVideoOutput(self._video_widget)
        self._media_player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._media_player.errorOccurred.connect(self._on_media_error)

        # Placeholder overlay (shown when no video is loaded)
        self._placeholder = QFrame()
        self._placeholder.setStyleSheet(
            """
            QFrame {
                border: 2px dashed #4b5563;
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.8);
                position: absolute;
            }
        """
        )
        self._placeholder.setParent(self._video_container)
        self._placeholder.setGeometry(
            10,
            10,
            self._video_container.width() - 20,
            self._video_container.height() - 20,
        )

        placeholder_layout = QVBoxLayout(self._placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setContentsMargins(20, 30, 20, 30)

        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon("fa5.play-circle", color="#6b7280").pixmap(48, 48)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("border: none; background: transparent;")

        drop_label = QLabel("Drop Video Here")
        drop_label.setStyleSheet(
            "color: #6b7280; font-size: 13px; border: none; background: transparent;"
        )
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint_label = QLabel("Drag & Drop")
        hint_label.setStyleSheet(
            "color: #4b5563; font-size: 11px; border: none; background: transparent;"
        )
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder_layout.addWidget(icon_label)
        placeholder_layout.addWidget(drop_label)
        placeholder_layout.addWidget(hint_label)

        root.addWidget(self._video_container)

        # ── Traffic Lights Footer ──
        lights_bar = QWidget()
        lights_bar.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 180);
            border: 1px solid #374151;
            border-radius: 8px;
        """
        )
        lights_layout = QHBoxLayout(lights_bar)
        lights_layout.setContentsMargins(12, 8, 12, 8)
        lights_layout.setSpacing(10)

        self._lights: dict[str, TrafficLightIndicator] = {}
        for color in ("red", "yellow", "green"):
            light = TrafficLightIndicator(color)
            light.clicked.connect(
                lambda checked=False, c=color: self._on_light_clicked(c)
            )
            self._lights[color] = light
            lights_layout.addWidget(light)

        # Set initial active light
        self._lights[self._active_light].set_active(True)

        lights_footer = QHBoxLayout()
        lights_footer.setContentsMargins(8, 0, 8, 8)
        lights_footer.addWidget(
            lights_bar,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        )

        video_layout.addLayout(lights_footer)

        # Initially show placeholder
        self._show_placeholder(True)

        # Load default video on init
        self._load_default_video()

    def _on_light_clicked(self, color: str):
        """Handle traffic light click events."""
        self._active_light = color
        for c, light in self._lights.items():
            light.set_active(c == color)
        self._timer_label.setText(f"{self.TIMERS[color]}s")

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            # Handle file drop
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(
                    (".mp4", ".avi", ".mov", ".mkv", ".mp3", ".wav")
                ):
                    self._load_video_file(file_path)
                    event.acceptProposedAction()
        elif event.mimeData().hasText():
            # Handle text drop (from review sidebar)
            video_name = event.mimeData().text()
            # Try video storage directory first, then absolute path
            possible_paths = [
                os.path.join(VIDEO_STORAGE_DIR, video_name),
                video_name,  # absolute path
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self._load_video_file(path)
                    event.acceptProposedAction()
                    return

            print(f"Video not found: {video_name}")

    def _show_placeholder(self, show: bool):
        """Show or hide the placeholder overlay."""
        self._placeholder.setVisible(show)
        self._video_widget.setVisible(not show)

    def _on_media_status_changed(self, status):
        """Handle media status changes."""
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self._show_placeholder(False)
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Loop the video
            self._media_player.setPosition(0)
            self._media_player.play()

    def _on_media_error(self, error, error_string):
        """Handle media playback errors."""
        print(f"Media error in Camera {self._camera_id}: {error_string}")
        self._show_placeholder(True)

    def _set_traffic_density(self, density: int):
        """Set traffic density level."""
        self._traffic_density = density
        # Here you could implement logic to switch to different videos based on density
        # For now, just update the UI
        print(f"Camera {self._camera_id}: Traffic density set to {density}")

    def _load_default_video(self):
        """Load the default video for this camera from config."""
        video_name = DEFAULT_VIDEOS.get(self._camera_id, "1.mp4")
        video_path = os.path.join(VIDEO_STORAGE_DIR, video_name)

        if os.path.exists(video_path):
            self._load_video_file(video_path)
        else:
            print(f"Default video not found: {video_path}")

    def _load_video_file(self, file_path: str):
        """Load a video file into the player (but don't play yet)."""
        if os.path.exists(file_path):
            self._current_video = file_path
            url = QUrl.fromLocalFile(file_path)
            self._media_player.setSource(url)
            print(f"Loaded video: {file_path} into Camera {self._camera_id}")
        else:
            print(f"Video file not found: {file_path}")

    def start_simulation(self):
        """Start video playback for simulation."""
        if self._current_video and os.path.exists(self._current_video):
            self._media_player.play()

    def stop_simulation(self):
        """Stop video playback."""
        self._media_player.pause()

    def get_traffic_density(self) -> int:
        """Get current traffic density level."""
        return self._traffic_density
