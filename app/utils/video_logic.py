"""
Video handling logic separated from UI (path normalization, validation, loading).
"""

import os
from app.config import DEFAULT_VIDEOS, VIDEO_STORAGE_DIR


def normalize_video_path(file_path):
    """Ensure video file paths work across different systems (like Windows)."""
    if os.name == "nt" and file_path.startswith("/") and ":" in file_path:
        return file_path.lstrip("/")
    return file_path


def is_valid_video_file(file_path):
    """Check if the path exists and is a common video type."""
    return os.path.exists(file_path) and file_path.lower().endswith(
        (".mp4", ".avi", ".mov", ".mkv")
    )


def get_full_video_path_from_name(dropped_text):
    """Convert a dropped filename or relative path into an absolute one."""
    possible_path = os.path.join(VIDEO_STORAGE_DIR, dropped_text)
    if not os.path.exists(possible_path):
        possible_path = dropped_text
    return os.path.abspath(possible_path)


def select_default_video_path(camera_id):
    """Find the best default video to load for a given camera ID."""
    video_name = DEFAULT_VIDEOS.get(camera_id, "1.mp4")
    local_path = os.path.abspath(os.path.join(VIDEO_STORAGE_DIR, video_name))
    backup_path = os.path.abspath(os.path.join("video", video_name))

    if os.path.exists(local_path):
        return local_path
    if os.path.exists(backup_path):
        return backup_path
    return None
