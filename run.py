#!/usr/bin/env python3
"""
Entry point for Traffic Control System
Run this script from the project root directory: python run.py
"""

if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")  # Add current directory to path

    from app.main import QApplication, QFont
    from app.ui import TrafficControlDashboard

    app = QApplication(sys.argv)

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = TrafficControlDashboard()
    window.show()
    sys.exit(app.exec())
