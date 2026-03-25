"""
Review Sidebar Widget Component (Modularized)
"""

import os
import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QListWidget,
    QAbstractItemView,
    QFileDialog,
    QInputDialog,
    QApplication,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import Qt, QMimeData, QUrl, QSize
from PySide6.QtGui import QColor, QDrag, QPixmap, QPainter

from app.config import VIDEO_STORAGE_DIR
from .video_item import VideoItem
from app.utils.sidebar_logic import (
    load_videos_from_json,
    add_video_to_json,
    get_video_thumbnail,
)


class ReviewSidebar(QWidget):
    """Left sidebar for reviewing and managing video files."""

    VIDEOS_JSON = "app/videos.json"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self._drag_start_pos = None
        self.setStyleSheet(
            "background-color: #1a1a1a; border-right: 1px solid #333333;"
        )

        # Video playback components
        self.media_player = QMediaPlayer()
        self.current_video_path = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("VIDEO REVIEW")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            """
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            padding: 4px;
            background-color: #2a2a2a;
            border-radius: 4px;
        """
        )

        # Add Video Button
        self.add_video_btn = QPushButton("ADD VIDEO")
        self.add_video_btn.setIcon(qta.icon("fa5s.plus", color="#ffffff"))
        self.add_video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_video_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
                font-weight: 700;
                margin-bottom: 4px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """
        )
        self.add_video_btn.clicked.connect(self._on_add_video_clicked)

        # Add YouTube Button
        self.add_yt_btn = QPushButton("ADD YOUTUBE")
        self.add_yt_btn.setIcon(qta.icon("fa5b.youtube", color="#ffffff"))
        self.add_yt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_yt_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
                font-weight: 700;
                margin-bottom: 8px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """
        )
        self.add_yt_btn.clicked.connect(self._on_add_yt_clicked)

        layout.addWidget(header)
        layout.addWidget(self.add_video_btn)
        layout.addWidget(self.add_yt_btn)

        # Video list
        self.video_list = QListWidget()
        self.video_list.setStyleSheet(
            """
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                color: #d1d5db;
                selection-background-color: #3a3a3a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
            }
        """
        )
        self.video_list.setIconSize(QSize(64, 48))
        self.video_list.setDragEnabled(False)
        self.video_list.setAcceptDrops(False)
        self.video_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Connect signals
        self.video_list.itemClicked.connect(self._on_video_selected)
        self.video_list.setDragEnabled(False)

        self._video_path_map = {}
        self._refresh_video_list()

        layout.addWidget(self.video_list)

        # Preview area label
        preview_label = QLabel("PREVIEW")
        preview_label.setStyleSheet(
            "color: #9ca3af; font-size: 12px; font-weight: 600; margin-top: 8px;"
        )
        layout.addWidget(preview_label)

        # Preview container
        self.preview_area = QFrame()
        self.preview_area.setFixedHeight(150)
        self.preview_area.setStyleSheet(
            "background-color: #000000; border: 2px dashed #4b5563; border-radius: 4px;"
        )

        preview_layout = QVBoxLayout(self.preview_area)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        # Placeholder for no video loaded
        self.preview_placeholder = QFrame()
        self.preview_placeholder.setStyleSheet(
            "border: none; background-color: transparent;"
        )
        placeholder_layout = QVBoxLayout(self.preview_placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preview_icon = QLabel()
        preview_icon.setPixmap(qta.icon("fa5.image", color="#6b7280").pixmap(40, 40))
        preview_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_icon.setStyleSheet("border: none; background-color: transparent;")

        preview_text = QLabel("Click video to preview")
        preview_text.setStyleSheet(
            "color: #6b7280; font-size: 11px; background-color: transparent;"
        )
        preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder_layout.addWidget(
            preview_icon, alignment=Qt.AlignmentFlag.AlignCenter
        )
        placeholder_layout.addWidget(
            preview_text, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000; border: none;")
        self.video_widget.setCursor(Qt.CursorShape.OpenHandCursor)
        self.video_widget.setToolTip("Drag this preview to replace a camera video")

        # Use lambda for short handlers
        self.video_widget.mousePressEvent = lambda ev: self._start_preview_drag(ev)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)

        # Add widgets to preview layout
        preview_layout.addWidget(self.preview_placeholder)
        preview_layout.addWidget(self.video_widget)
        self.video_widget.hide()

        layout.addWidget(self.preview_area)

        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)

        self.play_btn = QPushButton()
        self.play_btn.setIcon(qta.icon("fa5s.play", color="#60a5fa"))
        self.play_btn.setFixedSize(40, 28)
        self.play_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2a2a2a;
                color: #60a5fa;
                border: 1px solid #444444;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """
        )
        self.play_btn.clicked.connect(self._preview_play)

        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(qta.icon("fa5s.pause", color="#60a5fa"))
        self.pause_btn.setFixedSize(40, 28)
        self.pause_btn.setStyleSheet(self.play_btn.styleSheet())
        self.pause_btn.clicked.connect(self._preview_pause)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(qta.icon("fa5s.stop", color="#60a5fa"))
        self.stop_btn.setFixedSize(40, 28)
        self.stop_btn.setStyleSheet(self.play_btn.styleSheet())
        self.stop_btn.clicked.connect(self._preview_stop)

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)
        layout.addStretch()

    def _create_control_btn(self, icon, callback):
        btn = QPushButton()
        btn.setIcon(qta.icon(icon, color="#60a5fa"))
        btn.setFixedSize(40, 28)
        btn.setStyleSheet(
            "QPushButton { background-color: #2a2a2a; border: 1px solid #444444; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3a3a3a; }"
        )
        btn.clicked.connect(callback)
        return btn

    def _refresh_video_list(self):
        self.video_list.clear()
        self._video_path_map.clear()
        videos = load_videos_from_json(self.VIDEOS_JSON)
        for v in videos:
            name, path = v["name"], v["path"]
            self._video_path_map[name] = path
            icon = get_video_thumbnail(path) or qta.icon("fa5s.video", color="#6b7280")
            item = VideoItem(name, path, icon)
            item.setToolTip(f"Path: {path}")
            self.video_list.addItem(item)

    def _on_video_selected(self, item):
        if item:
            path = self._video_path_map.get(item.text())
            if path and os.path.exists(path):
                self._load_preview_video(path)

    def _on_add_video_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Video", os.getcwd(), "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            add_video_to_json(self.VIDEOS_JSON, os.path.basename(file_path), file_path)
            self._refresh_video_list()

    def _on_add_yt_clicked(self):
        url, ok = QInputDialog.getText(
            self,
            "Add YouTube",
            "URL:",
            text="https://www.youtube.com/watch?v=cJatWBDNabE",
        )
        if ok and url:
            print(f"YouTube download requested for {url}")
            # Implementation omitted for brevity in this UI pass

    def _load_preview_video(self, file_path):
        self.current_video_path = file_path
        self.preview_placeholder.hide()
        self.video_widget.show()
        self.media_player.stop()
        self.media_player.setSource(QUrl.fromLocalFile(os.path.abspath(file_path)))
        self.media_player.play()

    def _preview_play(self):
        self.media_player.play()

    def _preview_pause(self):
        self.media_player.pause()

    def _preview_stop(self):
        self.media_player.stop()
        self.media_player.setPosition(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.video_list.itemAt(self.video_list.mapFrom(self, event.pos()))
            if item:
                self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            not (event.buttons() & Qt.MouseButton.LeftButton)
            or not self._drag_start_pos
        ):
            return
        if (
            event.pos() - self._drag_start_pos
        ).manhattanLength() < QApplication.startDragDistance():
            return
        item = self.video_list.itemAt(self.video_list.mapFrom(self, event.pos()))
        if item:
            self._start_drag(item)
            self._drag_start_pos = None

    def _start_drag(self, item):
        self._execute_drag(item.text(), self._video_path_map[item.text()])

    def _start_preview_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_video_path:
            self._execute_drag(
                os.path.basename(self.current_video_path), self.current_video_path
            )

    def _execute_drag(self, name, path):
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(os.path.abspath(path))])
        mime.setText(name)
        drag = QDrag(self)
        drag.setMimeData(mime)
        pixmap = QPixmap(140, 50)
        pixmap.fill(QColor("#2a2a2a"))
        p = QPainter(pixmap)
        p.setPen(QColor("#60a5fa"))
        p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"Switch to {name}")
        p.end()
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

    def get_selected_video_path(self):
        current_item = self.video_list.currentItem()
        return self._video_path_map.get(current_item.text()) if current_item else None

    def get_selected_video(self):
        current_item = self.video_list.currentItem()
        return current_item.text() if current_item else None
