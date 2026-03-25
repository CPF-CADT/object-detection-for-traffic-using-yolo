
# Object Detection for Traffic Using YOLO (Dataset & Training)

This project preprocesses the UA-DETRAC dataset for vehicle detection using YOLOv8. It converts XML annotations to YOLO format, merges all vehicle classes into a single class, and subsamples frames for efficient training.

## Features
- Converts UA-DETRAC XML annotations to YOLO .txt format.
- Eliminates multiple vehicle classes (car, bus, etc.) into one class (vehicle).
- Subsamples frames (every 10th frame) to reduce dataset size.
- Splits data into train/val/test sets.

## Dataset
- **Source**: UA-DETRAC (Unmanned Aerial Vehicle - Traffic Surveillance) dataset.
- **Download**: Available from [UA-DETRAC official site](http://detrac-db.rit.albany.edu/) or mirrors. Extract to a `dataset/` folder with subfolders `DETRAC-Images/`, `DETRAC-Train-Annotations-XML/`, and `DETRAC-Test-Annotations-XML/`.
- **Note**: Dataset is ~140k frames; preprocessing reduces to ~14k images.

## Folder Structure
- `data_preprocessing.ipynb`: code to download, preprocess, and verify the dataset.
- `model_training.ipynb`: The actual YOLOv8 training loop and loss curve monitoring.
- `inference_and_counting.ipynb`: Implementing the "Line Crossing" logic and testing on video files.
- `export_model.ipynb`: Converting .pt to .onnx or TensorRT for backend.
- `requirements.txt`: List of Python dependencies required for the project.
- `dataset/`: Raw UA-DETRAC dataset (download and extract here).
  - `DETRAC-Images/`: Folders containing images for each video sequence (e.g., MVI_20011/).
  - `DETRAC-Train-Annotations-XML/`: XML annotation files for training sequences.
  - `DETRAC-Test-Annotations-XML/`: XML annotation files for test sequences.
- [`vehicle_dataset/`](https://cadtedu-my.sharepoint.com/:u:/g/personal/vathanak_phy_student_cadt_edu_kh/IQDqKsPhtMTJRYXtD4Qn_x2hAQbtoXY-8yWFvLUl4rtdyE8?e=y7NEQt): Processed dataset in YOLO format. It is organized into `images/` and `labels/` directories, each containing `train`, `val`, and `test` subfolders to ensure compatibility with YOLO training pipelines. Includes a `data.yaml` file for configuration.

## Installation
1. Clone the repo: `git clone https://github.com/CPF-CADT/object-detection-for-traffic-using-yolo.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Download and extract UA-DETRAC dataset as described above.

## Usage
1. Run the preprocessing notebook: Open `data_preprocessing.ipynb` in Jupyter and execute all cells.
2. This creates a `vehicle_dataset/` folder with YOLO-formatted data.
3. Train YOLO: Use Ultralytics YOLOv8 (e.g., `yolo train data=vehicle_dataset/data.yaml model=yolov8n.pt`).

##  Core Approach (The `app/` Engine)

<p align="center">
  <img src="https://res.cloudinary.com/dgnugtetz/image/upload/v1774466303/bdf97080-3b16-4ebf-9dd7-1bc2f58fd52a.png" alt="Traffic Detection UI" width="800">
</p>

*The dashboard displays real-time traffic monitoring, vehicle counting, and system performance metrics including CPU and GPU utilization.*

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

---
## Requirements
- Python 3.11.9
- See `requirements.txt` for dependencies.

## Results
- Processed 13,795 images: 7,353 train, 834 val, 5,608 test.
- All annotations in YOLO format with class 0 (vehicle).

## References

1. **UA-DETRAC dataset**  University at Albany DEtection and TRACking (UA-DETRAC) benchmark dataset. Official project page by Dawei Du: [https://sites.google.com/view/daweidu/projects/ua-detrac](https://sites.google.com/view/daweidu/projects/ua-detrac).  
   - The dataset consists of 100 real-world traffic videos (>140,000 frames) with detailed annotations for multi-object detection and tracking.  

2. **Citation**  Wen, L., Du, D., Cai, Z., Lei, Z., Chang, M.-C., Qi, H., Lim, J., Yang, M.-H., Lyu, S., *UA-DETRAC: A New Benchmark and Protocol for Multi-Object Detection and Tracking*, Computer Vision and Image Understanding (CVIU), 2020.  
   - DOI / journal link if desired: [https://doi.org/10.1016/j.cviu.2019.102907](https://doi.org/10.1016/j.cviu.2019.102907)  

3. **YOLOv8 (Ultralytics)**  Official YOLOv8 documentation for training, model usage, and exporting: [https://docs.ultralytics.com/](https://docs.ultralytics.com/).  

4. **Python libraries used**  OpenCV, Matplotlib, tqdm, etc. (for dataset processing, visualization, and progress tracking).
