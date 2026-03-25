"""
Traffic Control Dashboard — PySide6
Converted from React (App.tsx, CameraWidget.tsx, TrafficLight.tsx)
"""

import sys
import os

# Add parent directory to path to enable 'app' module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.ui import TrafficControlDashboard


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = TrafficControlDashboard()
    window.show()
    sys.exit(app.exec())
