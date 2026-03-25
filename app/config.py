"""
Configuration file for Traffic Control System
Edit this file to change default videos and settings
"""

# Default video mapping for each camera (camera_id: video_filename)
DEFAULT_VIDEOS = {
    1: "1.mp4",
    2: "2.mp4",
    3: "3.mp4",
    4: "1.mp4",  # Camera 4 reuses video 1
}

# Video storage directory
VIDEO_STORAGE_DIR = "app/videos"

# UI Settings
UI_SETTINGS = {
    "auto_play_on_start": False,  # Don't auto-play videos on app startup
    "loop_videos": True,  # Loop videos when they end
}
