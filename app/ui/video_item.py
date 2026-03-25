from PySide6.QtWidgets import QListWidgetItem


class VideoItem(QListWidgetItem):
    """Custom item with thumbnail support."""

    def __init__(self, name, path, icon=None):
        super().__init__(name)
        self._path = path
        if icon:
            self.setIcon(icon)
