"""
Camera Widget Component
"""

import os
import cv2
from matplotlib.pyplot import show
import numpy as np
from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QPushButton,
    QFileDialog,
)
from PySide6.QtCore import Qt, QUrl, QTimer, Slot
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QImage, QPixmap

from app.config import DEFAULT_VIDEOS, VIDEO_STORAGE_DIR
from app.yolo_worker import YoloWorker
from .traffic_light_indicator import TrafficLightIndicator
import qtawesome as qta


class VideoDropWidget(QLabel):
    """Subclass of QLabel to handle drag and drop and display YOLO results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._parent_widget = parent
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle dropped video with path normalization and header updates."""
        # 1. Handle File URLs (External files or Sidebar URLs)
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # Normalize Windows paths (fixes leading slash issues)
                if os.name == "nt" and file_path.startswith("/") and ":" in file_path:
                    file_path = file_path.lstrip("/")

                print(
                    f"DEBUG: Camera {getattr(self._parent_widget, '_camera_id', '?')} dropped URL: {file_path}"
                )

                if os.path.exists(file_path):
                    if hasattr(self._parent_widget, "_load_video_file"):
                        self._parent_widget._load_video_file(file_path)
                        event.acceptProposedAction()
                        return

        # 2. Handle Plain Text (Sidebar internal name fallback)
        if event.mimeData().hasText():
            dropped_text = event.mimeData().text().strip()
            possible_path = os.path.join(VIDEO_STORAGE_DIR, dropped_text)
            if not os.path.exists(possible_path):
                possible_path = dropped_text  # Try as absolute path

            print(
                f"DEBUG: Camera {getattr(self._parent_widget, '_camera_id', '?')} dropped Text: {possible_path}"
            )

            if os.path.exists(possible_path) and possible_path.lower().endswith(
                (".mp4", ".avi", ".mov", ".mkv")
            ):
                if hasattr(self._parent_widget, "_load_video_file"):
                    self._parent_widget._load_video_file(possible_path)
                    event.acceptProposedAction()
                    return

        event.ignore()


class CameraWidget(QFrame):
    """Reusable camera panel with specialized video drop area and YOLO detection."""

    TIMERS = {"red": 30, "yellow": 5, "green": 25}

    def __init__(self, camera_id: int, parent=None):
        super().__init__(parent)
        self._camera_id = camera_id
        self._active_light = "red"
        self._current_video = None
        self._simulation_running = False
        self._traffic_density = 0  # 0 = default/no cars, 1-4 = traffic levels
        self._yolo_worker = None
        self._model_path = os.path.abspath("models/yolov5_1k.pt")

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

        # Camera title/ID
        self._title_label = QLabel(f"Camera {camera_id}")
        self._title_label.setObjectName("camera_title")
        self._title_label.setStyleSheet(
            "color: #d1d5db; font-weight: 600; font-size: 14px; border: none;"
        )

        # File selection button
        self._load_btn = QPushButton()
        self._load_btn.setIcon(qta.icon("fa5s.folder-open", color="#9ca3af"))
        self._load_btn.setFixedSize(28, 28)
        self._load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._load_btn.setToolTip("Select video file for this camera")
        self._load_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
                border-color: #60a5fa;
            }
        """
        )
        self._load_btn.clicked.connect(self._on_load_clicked)

        # Quick Switch button (Replace with sidebar selection)
        self._switch_btn = QPushButton()
        self._switch_btn.setIcon(qta.icon("fa5s.exchange-alt", color="#9ca3af"))
        self._switch_btn.setFixedSize(28, 28)
        self._switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._switch_btn.setToolTip("Replace with video selected in sidebar")
        self._switch_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #333333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
                border-color: #60a5fa;
            }
        """
        )
        self._switch_btn.clicked.connect(self._on_switch_clicked)

        self._timer_label = QLabel(f"{self.TIMERS[self._active_light]}s")
        self._timer_label.setStyleSheet(
            "color: #ffffff; font-weight: 700; font-size: 20px; border: none;"
        )
        self._timer_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        header_layout.addWidget(self._title_label)
        header_layout.addSpacing(8)
        header_layout.addWidget(self._load_btn)
        header_layout.addSpacing(8)
        header_layout.addWidget(self._switch_btn)
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

        # Video widget for playback (Subclassed to display processed frames)
        self._video_widget = VideoDropWidget(self)
        self._video_widget.setStyleSheet("background-color: #000000;")
        video_layout.addWidget(self._video_widget, stretch=1)

        # Placeholder overlay (Doesn't block drops since VideoDropWidget is below it)
        self._placeholder = QFrame()
        self._placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
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

        # Enable drops
        self.setAcceptDrops(True)

        # Load default video on init
        self._load_default_video()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()

    def dropEvent(self, event: QDropEvent):
        # Redirect drop to the video widget's logic
        self._video_widget.dropEvent(event)

    def _on_light_clicked(self, color: str):
        """Handle traffic light click events."""
        self._active_light = color
        for c, light in self._lights.items():
            light.set_active(c == color)
        self._timer_label.setText(f"{self.TIMERS[color]}s")

    def _on_load_clicked(self):
        """Show file dialog to pick a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Video for Camera {self._camera_id}",
            os.getcwd(),
            "Video Files (*.mp4 *.avi *.mov *.mkv)",
        )
        if file_path:
            self._load_video_file(file_path)

    def _on_switch_clicked(self):
        """Replace this camera's video with the one selected in the sidebar."""
        # Find the main window to get sidebar access
        main_win = self.window()
        if hasattr(main_win, "review_sidebar"):
            selected_video_path = main_win.review_sidebar.get_selected_video_path()
            if selected_video_path and os.path.exists(selected_video_path):
                self._load_video_file(os.path.abspath(selected_video_path))
            else:
                print("DEBUG: No video selected or path invalid.")
        else:
            print("DEBUG: Sidebar not found in window.")

    @Slot(np.ndarray)
    def _display_frame(self, frame):
        """Convert BGR frame from YOLO to QImage and display it."""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img)
        self._video_widget.setPixmap(pixmap)

    def _on_worker_error(self, message):
        print(f"YOLO Worker Error (Camera {self._camera_id}): {message}")

    def _load_video_file(self, file_path: str):
        """Stop current processing and start YOLO worker for new video."""
        if self._yolo_worker:
            self._yolo_worker.stop()
            self._yolo_worker.deleteLater()

        self._current_video = file_path
        self._show_placeholder(False)
        self._title_label.setText(
            f"Camera {self._camera_id} - {os.path.basename(file_path)}"
        )

        # Create and start new worker
        self._yolo_worker = YoloWorker(self._model_path, file_path)
        self._yolo_worker.frame_ready.connect(self._display_frame)
        self._yolo_worker.error.connect(self._on_worker_error)
        self._yolo_worker.start()

    def _load_default_video(self):
        """Load the default video from config."""
        video_name = DEFAULT_VIDEOS.get(self._camera_id)
        if video_name:
            # Check localized storage first, then root video/ folder
            local_path = os.path.abspath(os.path.join(VIDEO_STORAGE_DIR, video_name))
            root_path = os.path.abspath(os.path.join("video", video_name))

            if os.path.exists(local_path):
                self._load_video_file(local_path)
            elif os.path.exists(root_path):
                self._load_video_file(root_path)

    def _show_placeholder(self, show: bool):
        self._placeholder.setVisible(show)
        if show:
            self._video_widget.setPixmap(QPixmap())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._placeholder.setGeometry(
            10,
            10,
            self._video_container.width() - 20,
            self._video_container.height() - 20,
        )

        """Show or hide the placeholder overlay."""
        self._placeholder.setVisible(show)

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
        # Ensure path is relative to the project root
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        video_path = os.path.join(
            project_root, VIDEO_STORAGE_DIR.replace("/", os.sep), video_name
        )

        if os.path.exists(video_path):
            self._load_video_file(video_path)
        else:
            # Try partial path just in case
            video_path = os.path.join(VIDEO_STORAGE_DIR, video_name)
            if os.path.exists(video_path):
                self._load_video_file(video_path)
            else:
                print(
                    f"Default video not found for Camera {self._camera_id}: {video_name}"
                )

    def _load_video_file(self, file_path: str):
        """Load a video file into the player (but don't play yet)."""
        print(f"DEBUG: CameraWidget._load_video_file called with: {file_path}")
        if os.path.exists(file_path):
            # Stop existing media before replacing to ensure clean switch
            self._media_player.stop()
            # Crucial: Reset the source to empty to force the media player to release the file
            self._media_player.setSource(QUrl())

            self._current_video = file_path
            # Use absolute path for QUrl to ensure reliability
            abs_path = os.path.abspath(file_path)
            url = QUrl.fromLocalFile(abs_path)

            print(f"DEBUG: Setting new source to: {url.toString()}")
            self._media_player.setSource(url)

            # Change header title to show the currently loaded file
            file_name = os.path.basename(file_path)
            self._title_label.setText(f"Camera {self._camera_id} - {file_name}")
            self._title_label.setStyleSheet(
                "color: #60a5fa; font-weight: 700; border: none;"
            )

            print(f"SUCCESS: Video loaded into Camera {self._camera_id}: {abs_path}")

            # Force hide placeholder immediately if status doesn't trigger it fast enough
            self._show_placeholder(False)

            # If simulation is already running, keep playback seamless.
            if self._simulation_running:
                print(
                    f"DEBUG: Simulation is running, calling play() for Camera {self._camera_id}"
                )
                self._media_player.play()
            else:
                self._media_player.pause()
                self._media_player.setPosition(0)
        else:
            print(f"ERROR: Video file not found: {file_path}")

    def start_simulation(self):
        """Start video playback for simulation."""
        self._simulation_running = True
        if self._current_video and os.path.exists(self._current_video):
            self._media_player.play()

    def stop_simulation(self):
        """Stop video playback."""
        self._simulation_running = False
        self._media_player.pause()

    def get_traffic_density(self) -> int:
        """Get current traffic density level."""
        return self._traffic_density
