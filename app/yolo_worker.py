"""
Machine Learning Worker Thread for YOLO Detection in PySide6.
"""

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal, Slot
from ultralytics import YOLO
import os


class YoloWorker(QThread):
    """
    Worker thread that reads a video file, runs YOLO detection on each frame,
    and emits the processed frame and car count as a signal.
    """

    frame_ready = Signal(np.ndarray, int)  # frame, car_count
    finished = Signal()
    error = Signal(str)

    def __init__(self, model_path, video_source, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self.video_source = video_source
        self._running = False
        self._paused = False
        self.model = None

    def pause(self):
        """Pause the video processing."""
        self._paused = True

    def resume(self):
        """Resume the video processing."""
        self._paused = False

    def stop(self):
        """Stop the worker thread processing."""
        self._running = False
        self._paused = False
        self.wait()

    def run(self):
        self._running = True

        # Load model inside the thread to avoid issues
        try:
            if not os.path.exists(self.model_path):
                self.error.emit(f"Model file not found: {self.model_path}")
                return

            self.model = YOLO(self.model_path)

            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                self.error.emit(f"Could not open video source: {self.video_source}")
                return

            last_annotated_frame = None

            while self._running:
                # If NOT paused (Green/Yellow), we read a NEW frame
                if not self._paused:
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                    self._last_frame = frame
                else:
                    # In RED light, we REUSE the last frame captured before pausing
                    # This guarantees the video visually stops (no movement)
                    if hasattr(self, "_last_frame") and self._last_frame is not None:
                        frame = self._last_frame
                    else:
                        # Fallback for first run
                        ret, frame = cap.read()
                        self._last_frame = frame

                # YOLO ALWAYS scans the current frame (either moving or static)
                # to keep vehicle counts updated for the dynamic controller.
                frame_inference = cv2.resize(frame, (640, 480))
                results = self.model.predict(
                    source=frame_inference, conf=0.5, save=False, verbose=False
                )

                results_data = results[0]
                annotated_frame = results_data.plot()

                # Count detected objects (Class 0 = Vehicle)
                car_count = 0
                if results_data.boxes is not None:
                    classes = results_data.boxes.cls.cpu().numpy()
                    car_count = sum([1 for c in classes if int(c) == 0])

                # Emit the frame and count
                self.frame_ready.emit(annotated_frame, car_count)

                # Control frame rate slightly to avoid 100% CPU on hold
                if self._paused:
                    self.msleep(100)  # Scan every 100ms when stopped
                else:
                    self.msleep(30)  # ~30fps when running

            cap.release()
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
