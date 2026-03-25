"""
Configuration file for Traffic Control System
Edit this file to change default videos and settings
"""

# Default video mapping for each camera (camera_id: video_filename)
DEFAULT_VIDEOS = {
    1: "1.mp4",
    2: "2.mp4",
    3: "53125-472583428_medium.mp4",
    4: "1.mp4",  # Camera 4 reuses video 1
}

# Video storage directory
VIDEO_STORAGE_DIR = "app/videos"

# UI Settings
UI_SETTINGS = {
    "auto_play_on_start": False,  # Don't auto-play videos on app startup
    "loop_videos": True,  # Loop videos when they end
}

# Default Traffic Light Timers (in seconds)
# These represent the base values for the simulation phase
TRAFFIC_LIGHT_SETTINGS = {
    "default_red": 30,
    "default_yellow": 3,
    "default_green": 25,
    "all_red_delay": 1,  # Safety gap between transitions
}

# Per-camera default green light overrides (camera_id: max_green_seconds)
CAMERA_GREEN_DEFAULTS = {1: 5, 2: 5, 3: 2, 4: 2}  # North  # West  # East  # South
