import json
import os
import yt_dlp
import cv2
from PySide6.QtGui import QIcon, QImage, QPixmap
from app.config import VIDEO_STORAGE_DIR


def load_videos_from_json(videos_json_path):
    """Load video references from JSON file."""
    if not os.path.exists(videos_json_path):
        initial_data = []
        if os.path.exists(VIDEO_STORAGE_DIR):
            for f in os.listdir(VIDEO_STORAGE_DIR):
                if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    initial_data.append(
                        {"name": f, "path": os.path.join(VIDEO_STORAGE_DIR, f)}
                    )
        with open(videos_json_path, "w") as f:
            json.dump(initial_data, f, indent=4)

    try:
        with open(videos_json_path, "r") as f:
            videos = json.load(f)
            processed_videos = []
            for v in videos:
                name = v.get("name")
                path = v.get("path")
                if name and path:
                    if not os.path.isabs(path):
                        path = os.path.abspath(os.path.join(VIDEO_STORAGE_DIR, path))
                    processed_videos.append({"name": name, "path": path})
            return processed_videos
    except Exception as e:
        print(f"Error loading {videos_json_path}: {e}")
        return []


def get_video_thumbnail(path):
    """Extract a thumbnail from the video file."""
    if not os.path.exists(path):
        return None

    try:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return None

        cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.resize(frame, (64, 48))
            h, w, ch = frame.shape
            q_img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_BGR888)
            return QIcon(QPixmap.fromImage(q_img))
    except:
        pass
    return None


def add_video_to_json(videos_json_path, name, path):
    """Helper to add video metadata to JSON."""
    videos = []
    if os.path.exists(videos_json_path):
        try:
            with open(videos_json_path, "r") as f:
                videos = json.load(f)
        except:
            pass

    abs_path = os.path.abspath(path)
    if not any(v.get("path") == abs_path for v in videos):
        videos.append({"name": name, "path": abs_path})
        with open(videos_json_path, "w") as f:
            json.dump(videos, f, indent=4)
        return True
    return False


async def download_youtube_video(url, progress_callback):
    """Download YouTube video using yt-dlp."""
    if not os.path.exists(VIDEO_STORAGE_DIR):
        os.makedirs(VIDEO_STORAGE_DIR)

    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": os.path.join(VIDEO_STORAGE_DIR, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_callback],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path, os.path.basename(file_path)
