import os
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from app.utils.video_logic import (
    normalize_video_path,
    is_valid_video_file,
    get_full_video_path_from_name,
)


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
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = normalize_video_path(urls[0].toLocalFile())
                if is_valid_video_file(file_path):
                    if hasattr(self._parent_widget, "_load_video_file"):
                        self._parent_widget._load_video_file(file_path)
                        event.acceptProposedAction()
                        return

        if event.mimeData().hasText():
            dropped_text = event.mimeData().text().strip()
            possible_path = get_full_video_path_from_name(dropped_text)
            if is_valid_video_file(possible_path):
                if hasattr(self._parent_widget, "_load_video_file"):
                    self._parent_widget._load_video_file(possible_path)
                    event.acceptProposedAction()
                    return
        event.ignore()
