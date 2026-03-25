"""
Global Traffic Logic Controller
Coordinates sequential light phases across multiple cameras.
"""

from PySide6.QtCore import QObject, QTimer, Slot
from app.config import TRAFFIC_LIGHT_SETTINGS, CAMERA_GREEN_DEFAULTS
from app.utils.traffic_logic import recalculate_green_durations


class GlobalTrafficController(QObject):
    """Manages the dynamic traffic flow based on YOLO car counts."""

    # Using imported settings for global logic
    TRANSITION_DELAY = int(TRAFFIC_LIGHT_SETTINGS.get("all_red_delay", 1.5) * 1000)

    # Defaults fetched from config
    DEFAULT_MAX_GREEN = [
        CAMERA_GREEN_DEFAULTS.get(1, 30),
        CAMERA_GREEN_DEFAULTS.get(2, 45),
        CAMERA_GREEN_DEFAULTS.get(3, 30),
        CAMERA_GREEN_DEFAULTS.get(4, 20),
    ]

    def __init__(self, camera_widgets: list, parent=None):
        super().__init__(parent)
        self.cameras = camera_widgets
        self._current_idx = 0
        self._is_running = False

        # Current green durations (smoothed)
        self._current_green_times = [float(t) for t in self.DEFAULT_MAX_GREEN]

        # Periodic update timer for dynamic adjustment
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(2000)  # Update every 2 seconds
        self._update_timer.timeout.connect(self._recalculate_green_times)

        # Connect signals
        for i, cam in enumerate(self.cameras):
            cam.cycle_finished.connect(self._on_camera_cycle_finished)

    def start(self):
        """Start the global traffic cycle."""
        self._is_running = True
        self._current_idx = 0  # Points to Index 0 (Camera 1)

        # Start dynamic updates
        self._update_timer.start()

        # Recalculate once immediately using current YOLO detections
        self._recalculate_green_times()

        # Start the first camera
        self._activate_next()

    def stop(self):
        """Stop the cycle."""
        self._is_running = False
        self._update_timer.stop()

    def _recalculate_green_times(self):
        """Dynamic calculation based on car counts."""
        if not self._is_running:
            return

        car_counts = [cam._car_count for cam in self.cameras]

        # Call business logic from utils
        self._current_green_times = recalculate_green_durations(
            self._current_green_times, car_counts, self.DEFAULT_MAX_GREEN
        )

        # Print debug log
        print("\n--- DYNAMIC TRAFFIC UPDATE ---")
        for i, cam in enumerate(self.cameras):
            # Update camera UI settings with the logic result
            final_sec = int(self._current_green_times[i])
            cam.header.timer_input.setValue(final_sec)

            # LIVE INJECTION: Only apply if currently Green
            if cam._active_light == "green":
                if final_sec < cam._remaining_time:
                    cam._remaining_time = final_sec

            print(
                f"Cam {i+1}: D:{self.DEFAULT_MAX_GREEN[i]}s | C:{cam._car_count} Cars | G:{final_sec}s"
            )
        print("----------------------------\n")

    def _activate_next(self):
        """Activate the next camera in a strict 1-2-3-4 sequence."""
        if not self._is_running:
            return

        # 1. Skip logic for the *current* target in the loop
        cam = self.cameras[self._current_idx]
        if cam._car_count == 0:
            print(
                f"DEBUG: Camera {cam._camera_id} is empty. Skipping to next in sequence..."
            )
            self._current_idx = (self._current_idx + 1) % len(self.cameras)
            # Short delay for skip animation/log
            QTimer.singleShot(500, self._activate_next)
            return

        print(
            f"DEBUG: Activating green for Camera {cam._camera_id} ({cam._car_count} cars)"
        )

        # 2. Apply the dynamic green time from YOLO brain
        optimized_green = int(self._current_green_times[self._current_idx])
        cam.TIMERS["green"] = optimized_green
        cam.header.timer_input.setValue(optimized_green)

        # Force state change
        cam.set_light("GREEN")

    @Slot(int)
    def _on_camera_cycle_finished(self, camera_id):
        """Called when a camera finishes its Green + Yellow phase."""
        if not self._is_running:
            return

        # --- SMART HOLD LOGIC ---
        # Check if there are ANY cars waiting on the other 3 roads
        other_cars = sum(
            self.cameras[i]._car_count
            for i in range(len(self.cameras))
            if i != self._current_idx
        )

        current_cam = self.cameras[self._current_idx]

        # If no one is waiting on other roads, and current road still has traffic,
        # RENEW the green light instead of turning Red.
        if other_cars == 0 and current_cam._car_count > 0:
            print(
                f"DEBUG: No cars on other roads. Holding GREEN for Camera {camera_id}..."
            )
            # Give a small 5-second extension to keep moving
            current_cam.TIMERS["green"] = 5
            current_cam.set_light("GREEN")
            return
        # ------------------------

        # Ensure the camera that just finished is set to RED
        finished_cam = self.cameras[self._current_idx]
        finished_cam.set_light("RED")

        # Move to next index (Strict C1 -> C2 -> C3 -> C4)
        self._current_idx = (self._current_idx + 1) % len(self.cameras)

        # Wait a bit (All Red transition) before starting next
        print(
            f"DEBUG: All Red phase for {self.TRANSITION_DELAY}ms before Camera {self._current_idx + 1}"
        )
        QTimer.singleShot(self.TRANSITION_DELAY, self._activate_next)
