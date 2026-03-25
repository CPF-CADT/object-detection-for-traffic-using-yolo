# Smart Traffic Management System with YOLOv5

This repository contains a high-performance, real-time traffic control and monitoring system using YOLOv5 for object detection. It features a sophisticated PySide6-based dashboard for intersection simulation, dynamic traffic light logic, and multi-camera orchestration.

##  Core Approach (The `app/` Engine)
The application follows a modular, signal-driven architecture to simulate a 4-way intersection controlled by AI:

1.  **Multi-Threaded Processing (`yolo_worker.py`)**: 
    - Each camera runs on a dedicated `QThread` to ensure the UI remains responsive.
    - Uses **GPU Acceleration** (via CUDA) for real-time inference on the `yolov5_1k.pt` model.
    - Emits live annotated frames and car counts back to the main UI.

2.  **Global Traffic Controller (`global_controller.py`)**:
    - Coordinates the 4-way cycle (CAM 1  CAM 2  CAM 3  CAM 4).
    - **Dynamic Timing**: Automatically adjusts Green light duration based on the number of vehicles detected.
    - **Smart Logic**:
        - **Skip Empty Roads**: If a camera detects 0 cars, it skips its cycle immediately.
        - **Extend Green**: If no cars are waiting on other roads, the current camera stays green to maximize flow.
        - **Zero-Wait Transition**: Skips the Yellow/Red phase entirely if the intersection is empty elsewhere.

3.  **Process-Isolated Monitoring (`system_monitor.py`)**:
    - Tracks CPU Cores, RAM (RSS), and GPU Memory usage specific to this Python process.
    - Designed for hardware benchmarking and performance comparison across different machines.

##  Features and Capabilities

###  Simulation & UI
- **4-Way Intersection Grid**: Real-time synchronized playback and detection of 4 video feeds.
- **Interactive Controls**: Manual light switching (Red/Yellow/Green) and video playback controls.
- **Drag-and-Drop Video**: Easily swap out traffic footage for any of the 4 cameras via the UI sidebar.
- **Navigation Compass**: A clean, "Navigation Style" UI that maps C1-C4 to cardinal directions (NWSE) with live active highlighting.

###  AI & Logic
- **YOLOv5 Integration**: Optimized for vehicle detection (Car, Bus, Truck merged into one "Vehicle" class).
- **Auto-GPU Switching**: Detects your hardware and automatically forces CUDA/GPU usage for maximum FPS.
- **Traffic Smoothing**: Implements weighted moving averages to prevent flickering in light durations during detection.

##  Folder Structure
- `app/`: The core application engine.
  - `ui/`: PySide6 components (Dashboard, Compass, Monitor, etc.).
  - `utils/`: Business logic for traffic smoothing and system metrics.
  - `global_controller.py`: The "Brain" that manages the intersection cycles.
- `models/`: Pre-trained YOLOv5 weights (`.pt` files).
- `dataset/`: Training and preprocessing scripts for the UA-DETRAC dataset.
- `run.py`: Entry point to launch the Smart Traffic Dashboard.

##  Getting Started
1. **Clone the repo**: `git clone https://github.com/CPF-CADT/object-detection-for-traffic-using-yolo.git`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Launch the Dashboard**: `python run.py`

##  Requirements
- **OS**: Windows (tested) / Linux / macOS.
- **Python**: 3.11+
- **Hardware**: NVIDIA GPU (Optional but recommended for >30fps).

##  References
- **UA-DETRAC Benchmark**: Real-world traffic surveillance dataset.
- **Ultralytics YOLO**: The engine behind the detection logic.
