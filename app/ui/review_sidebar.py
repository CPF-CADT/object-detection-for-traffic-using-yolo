"""
Review Sidebar Widget Component
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QColor, QDrag, QPixmap, QPainter
import qtawesome as qta
import os
from app.config import VIDEO_STORAGE_DIR


class ReviewSidebar(QWidget):
    """Left sidebar for reviewing and managing video files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
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
            margin-bottom: 8px;
            padding: 4px;
            background-color: #2a2a2a;
            border-radius: 4px;
        """
        )
        layout.addWidget(header)

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
        self.video_list.setDragEnabled(True)
        self.video_list.setAcceptDrops(False)
        self.video_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Connect signals
        self.video_list.itemPressed.connect(self._start_drag)
        self.video_list.itemClicked.connect(self._on_video_selected)

        # Add videos from storage directory
        if os.path.exists(VIDEO_STORAGE_DIR):
            for file_name in os.listdir(VIDEO_STORAGE_DIR):
                if file_name.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    item = QListWidgetItem(file_name)
                    item.setToolTip(
                        f"Click to preview or drag to camera view: {file_name}"
                    )
                    self.video_list.addItem(item)

        layout.addWidget(self.video_list)

        # Preview area label
        preview_label = QLabel("PREVIEW")
        preview_label.setStyleSheet(
            """
            color: #9ca3af;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        """
        )
        layout.addWidget(preview_label)

        # Preview container
        self.preview_area = QFrame()
        self.preview_area.setFixedHeight(150)
        self.preview_area.setStyleSheet(
            """
            QFrame {
                background-color: #000000;
                border: 2px dashed #4b5563;
                border-radius: 4px;
            }
        """
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

        placeholder_layout.addWidget(preview_icon)
        placeholder_layout.addWidget(preview_text)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000; border: none;")
        self.media_player.setVideoOutput(self.video_widget)

        # Add widgets to preview layout (initially show placeholder)
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

    def _on_video_selected(self, item):
        """Called when a video is clicked in the list."""
        if item:
            video_name = item.text()
            video_path = os.path.join(VIDEO_STORAGE_DIR, video_name)
            if os.path.exists(video_path):
                self._load_preview_video(video_path)

    def _load_preview_video(self, file_path):
        """Load selected video into the preview widget."""
        if not os.path.exists(file_path):
            return

        self.current_video_path = file_path

        # Hide placeholder, show video widget
        self.preview_placeholder.hide()
        self.video_widget.show()

        # Load video into media player
        url = QUrl.fromLocalFile(os.path.abspath(file_path))
        self.media_player.setSource(url)
        self.media_player.play()

    def _preview_play(self):
        """Play the loaded preview video."""
        if self.current_video_path and self.media_player.source() != QUrl():
            self.media_player.play()

    def _preview_pause(self):
        """Pause the preview video."""
        if self.media_player.isPlaying():
            self.media_player.pause()

    def _preview_stop(self):
        """Stop the preview video and reset."""
        self.media_player.stop()
        self.media_player.setPosition(0)

    def _start_drag(self, item):
        """Start drag operation for video item."""
        if item:
            mime_data = QMimeData()
            mime_data.setText(item.text())

            drag = QDrag(self)
            drag.setMimeData(mime_data)

            # Create a pixmap for drag visualization
            pixmap = QPixmap(100, 50)
            pixmap.fill(QColor("#2a2a2a"))
            painter = QPainter(pixmap)
            painter.setPen(QColor("#60a5fa"))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, item.text())
            painter.end()

            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.CopyAction)

    def get_selected_video(self):
        """Get the currently selected video file name."""
        current_item = self.video_list.currentItem()
        if current_item:
            return current_item.text()
        return None
