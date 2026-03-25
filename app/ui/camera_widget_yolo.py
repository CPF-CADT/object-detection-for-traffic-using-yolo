"""
Camera Widget Component (Modularized)
"""

import os
import cv2
import numpy as np
import qtawesome as qta
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
from PySide6.QtCore import Qt, Slot, QTimer, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QImage, QPixmap

from app.config import (
    DEFAULT_VIDEOS,
    VIDEO_STORAGE_DIR,
    TRAFFIC_LIGHT_SETTINGS,
    CAMERA_GREEN_DEFAULTS,
)
from app.yolo_worker import YoloWorker
from .traffic_light_indicator import TrafficLightIndicator
from .camera_header import CameraHeader
from .video_drop_widget import VideoDropWidget
from .camera_placeholder import CameraPlaceholder
from app.utils.ui_helpers import STYLES, create_vbox_layout, create_hbox_layout
from app.utils.light_logic import (
    get_light_timers,
    calculate_new_timer_after_setting_changed,
)
from app.utils.video_logic import select_default_video_path


class CameraWidget(QFrame):
    """Reusable camera panel with YOLO detection."""

    cycle_finished = Signal(int)  # Emits camera_id when green/yellow cycle ends

    def __init__(self, camera_id: int, parent=None):
        super().__init__(parent)
        self._camera_id = camera_id

        # Logic: Get config-based timers from logic utility
        self.TIMERS = get_light_timers(
            camera_id, TRAFFIC_LIGHT_SETTINGS, CAMERA_GREEN_DEFAULTS
        )

        self._active_light = "red"
        self._current_video = None
        self._simulation_running = False
        self._yolo_worker = None
        self._car_count = 0
        self._model_path = os.path.abspath("models/yolov5_1k.pt")
        self._remaining_time = self.TIMERS[self._active_light]

        # Setup Main Layout
        self.setStyleSheet(STYLES["panel"])
        self.setMinimumSize(400, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = create_vbox_layout(margins=(0, 0, 0, 0), spacing=0)
        self.setLayout(root)

        # ── Header ──
        self.header = CameraHeader(
            camera_id,
            on_load=self._on_load_clicked,
            on_switch=self._on_switch_clicked,
            on_timer_change=self._on_timer_setting_changed,
            parent=self,
        )
        self.header.timer_input.setValue(self.TIMERS["green"])
        root.addWidget(self.header)

        # ── Video & Placeholder ──
        self._video_container = QWidget()
        self._video_container.setStyleSheet("background-color: #000000; border: none;")
        self._video_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        video_layout = create_vbox_layout(margins=(0, 0, 0, 0), spacing=0)
        self._video_container.setLayout(video_layout)

        self._video_widget = VideoDropWidget(self)
        video_layout.addWidget(self._video_widget, stretch=1)

        self._placeholder = CameraPlaceholder(self._video_container)

        root.addWidget(self._video_container)

        # ── Traffic Lights Footer (Floating style) ──
        lights_bar = QWidget()
        lights_bar.setFixedHeight(50)
        lights_bar.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); border: 1px solid #374151; border-radius: 8px;"
        )

        lights_layout = create_hbox_layout(margins=(12, 4, 12, 4), spacing=10)
        lights_bar.setLayout(lights_layout)

        self._lights: dict[str, TrafficLightIndicator] = {}
        for color in ("red", "yellow", "green"):
            light = TrafficLightIndicator(color)
            light.clicked.connect(
                lambda checked=False, c=color: self._on_light_clicked(c)
            )
            self._lights[color] = light
            lights_layout.addWidget(light)

        self._lights[self._active_light].set_active(True)

        lights_footer = create_hbox_layout(margins=(8, 0, 8, 8))
        lights_footer.addWidget(
            lights_bar,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        )
        video_layout.addLayout(lights_footer)

        # Timers
        self._cycle_timer = QTimer(self)
        self._cycle_timer.setInterval(1000)
        self._cycle_timer.timeout.connect(self._timer_tick)

        self._show_placeholder(True)
        self.setAcceptDrops(True)
        self._load_default_video()

    def set_light(self, color: str):
        self._on_light_clicked(color.lower())

    def _on_light_clicked(self, color: str):
        if hasattr(self, "_active_light") and self._active_light == color:
            return

        self._active_light = color
        self._remaining_time = self.TIMERS.get(color, 10)
        for c, light in self._lights.items():
            light.set_active(c == color)

        if color == "red":
            self.header.timer_label.hide()
            if self._yolo_worker:
                self._yolo_worker.pause()
        else:
            self.header.timer_label.show()
            self.header.timer_label.setText(f"{self._remaining_time}s")
            if self._yolo_worker:
                self._yolo_worker.resume()

    def _on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", os.getcwd(), "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            self._load_video_file(file_path)

    def _on_switch_clicked(self):
        main_win = self.window()
        if hasattr(main_win, "review_sidebar"):
            path = main_win.review_sidebar.get_selected_video_path()
            if path and os.path.exists(path):
                self._load_video_file(os.path.abspath(path))

    def _timer_tick(self):
        if not self._simulation_running:
            return
        if self._remaining_time > 0:
            self._remaining_time -= 1
            if self._active_light != "red":
                self.header.timer_label.setText(f"{self._remaining_time}s")
                self.header.timer_label.show()
            else:
                self.header.timer_label.hide()
        else:
            if self._active_light == "green":
                self._on_light_clicked("yellow")
            elif self._active_light == "yellow":
                self._on_light_clicked("red")
                self.cycle_finished.emit(self._camera_id)

    def _on_timer_setting_changed(self, value):
        self.TIMERS["green"] = value
        self._remaining_time = calculate_new_timer_after_setting_changed(
            "green", self._active_light, value, self._remaining_time
        )
        if self._active_light == "green":
            self.header.timer_label.setText(f"{value}s")

    @Slot(np.ndarray, int)
    def _display_frame(self, frame, car_count):
        self._car_count = car_count
        self.header.count_badge.setText(f"{car_count} Vehicles")
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        self._video_widget.setPixmap(QPixmap.fromImage(q_img))

    def _load_video_file(self, file_path: str):
        if self._yolo_worker:
            self._yolo_worker.stop()
            self._yolo_worker.deleteLater()
            self._yolo_worker = None

        self._current_video = file_path
        self._show_placeholder(False)
        self.header.title_label.setText(
            f"Camera {self._camera_id} - {os.path.basename(file_path)}"
        )
        self.header.title_label.setStyleSheet(
            "color: #60a5fa; font-weight: 700; border: none;"
        )

        self._yolo_worker = YoloWorker(self._model_path, file_path)
        self._yolo_worker.frame_ready.connect(self._display_frame)
        self._yolo_worker.error.connect(lambda msg: print(f"YOLO Error: {msg}"))
        self._yolo_worker.pause()
        self._yolo_worker.start()

    def _load_default_video(self):
        path = select_default_video_path(self._camera_id)
        if path:
            self._load_video_file(path)

    def _show_placeholder(self, show: bool):
        self._placeholder.setVisible(show)
        if show:
            self._video_widget.setPixmap(QPixmap())
            if self._yolo_worker:
                self._yolo_worker.stop()
                self._yolo_worker = None

    def start_simulation(self):
        self._simulation_running = True
        self._cycle_timer.start()
        if self._yolo_worker and not self._yolo_worker.isRunning():
            self._yolo_worker.start()

    def stop_simulation(self):
        self._simulation_running = False
        self._cycle_timer.stop()
        if self._yolo_worker:
            self._yolo_worker.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._placeholder.setGeometry(
            10,
            10,
            self._video_container.width() - 20,
            self._video_container.height() - 20,
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()

    def dropEvent(self, event: QDropEvent):
        self._video_widget.dropEvent(event)

    def closeEvent(self, event):
        if self._yolo_worker:
            self._yolo_worker.stop()
        super().closeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()

    def dropEvent(self, event: QDropEvent):
        self._video_widget.dropEvent(event)

    def set_light(self, color: str):
        """Public interface to set the light state (color: RED, YELLOW, GREEN)"""
        # Accept both uppercase and lowercase
        self._on_light_clicked(color.lower())

    def _on_light_clicked(self, color: str):
        # Prevent redundant state changes if already in this state
        if hasattr(self, "_active_light") and self._active_light == color:
            return

        self._active_light = color
        self._remaining_time = self.TIMERS.get(color, 10)
        for c, light in self._lights.items():
            light.set_active(c == color)

        # Sync video playback and timer visibility with lights
        if color == "red":
            # RED: Hide timer as requested, stop car movement
            self.header.timer_label.hide()
            if self._yolo_worker:
                self._yolo_worker.pause()
        else:
            # GREEN or YELLOW: Show timer, resume movement
            self.header.timer_label.show()
            self.header.timer_label.setText(f"{self._remaining_time}s")
            if self._yolo_worker:
                self._yolo_worker.resume()

    def _on_timer_tick(self):
        """Standard timer callback for countdowns."""
        if self._remaining_time > 0:
            self._remaining_time -= 1
            self.header.timer_label.setText(f"{self._remaining_time}s")

            # Auto-transition logic for Yellow -> Red handled by Controller signals,
            # but we emit here just in case of manual mode
            if self._remaining_time == 0:
                if self._active_light == "yellow":
                    self.cycle_finished.emit(self._camera_id)
        else:
            self.header.timer_label.setText("0s")

    def _on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Video",
            os.getcwd(),
            "Video Files (*.mp4 *.avi *.mov *.mkv)",
        )
        if file_path:
            self._load_video_file(file_path)

    def _on_switch_clicked(self):
        main_win = self.window()
        if hasattr(main_win, "review_sidebar"):
            path = main_win.review_sidebar.get_selected_video_path()
            if path and os.path.exists(path):
                self._load_video_file(os.path.abspath(path))

    def _timer_tick(self):
        """Countdown the current light timer."""
        if not self._simulation_running:
            return

        if self._remaining_time > 0:
            self._remaining_time -= 1
            # Only update label if NOT Red
            if self._active_light != "red":
                self.header.timer_label.setText(f"{self._remaining_time}s")
                self.header.timer_label.show()
            else:
                self.header.timer_label.hide()
        else:
            # Phase change
            if self._active_light == "green":
                self._on_light_clicked("yellow")
            elif self._active_light == "yellow":
                self._on_light_clicked("red")
                self.cycle_finished.emit(self._camera_id)
            # Red light waiting is handled by the GlobalController starting the next green

    def _on_timer_setting_changed(self, value):
        """Update the green timer value for this camera."""
        self.TIMERS["green"] = value
        if self._active_light == "green":
            self._remaining_time = value
            self.header.timer_label.setText(f"{value}s")

    @Slot(np.ndarray, int)
    def _display_frame(self, frame, car_count):
        self._car_count = car_count
        self.header.count_badge.setText(f"{car_count} Vehicles")

        # Always update the visual video frame to show the current state (preview)
        # We handle the "stopped in red" effect by just letting it run,
        # or you can toggle this back if you want it frozen.
        # For previewing a loaded video before starting, it needs to update.
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        self._video_widget.setPixmap(QPixmap.fromImage(q_img))

    def _on_worker_error(self, message):
        print(f"YOLO Error: {message}")

    def _load_video_file(self, file_path: str):
        if self._yolo_worker:
            self._yolo_worker.stop()
            self._yolo_worker.deleteLater()
            self._yolo_worker = None

        self._current_video = file_path
        self._show_placeholder(False)
        self.header.title_label.setText(
            f"Camera {self._camera_id} - {os.path.basename(file_path)}"
        )
        self.header.title_label.setStyleSheet(STYLES["title"] + " color: #60a5fa;")

        self._yolo_worker = YoloWorker(self._model_path, file_path)
        self._yolo_worker.frame_ready.connect(self._display_frame)
        self._yolo_worker.error.connect(self._on_worker_error)

        # Sync initial start state:
        # Always start in PAUSED (frozen) mode for the preview scan
        self._yolo_worker.pause()
        self._yolo_worker.start()

    def _load_default_video(self):
        video_name = DEFAULT_VIDEOS.get(self._camera_id, "1.mp4")
        local_path = os.path.abspath(os.path.join(VIDEO_STORAGE_DIR, video_name))
        root_path = os.path.abspath(os.path.join("video", video_name))
        path = local_path if os.path.exists(local_path) else root_path
        if os.path.exists(path):
            self._load_video_file(path)

    def _show_placeholder(self, show: bool):
        self._placeholder.setVisible(show)
        if show:
            self._video_widget.setPixmap(QPixmap())
            if self._yolo_worker:
                self._yolo_worker.stop()
                self._yolo_worker = None

    def start_simulation(self):
        self._simulation_running = True
        self._cycle_timer.start()
        if self._yolo_worker and not self._yolo_worker.isRunning():
            self._yolo_worker.start()

    def stop_simulation(self):
        self._simulation_running = False
        self._cycle_timer.stop()
        if self._yolo_worker:
            self._yolo_worker.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._placeholder.setGeometry(
            10,
            10,
            self._video_container.width() - 20,
            self._video_container.height() - 20,
        )

    def closeEvent(self, event):
        if self._yolo_worker:
            self._yolo_worker.stop()
        super().closeEvent(event)
