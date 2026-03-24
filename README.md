# Object Detection for Traffic Using YOLO

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

## Requirements
- Python 3.11.9
- See `requirements.txt` for dependencies.

## Results
- Processed 13,795 images: 7,353 train, 834 val, 5,608 test.
- All annotations in YOLO format with class 0 (vehicle).

## References

1. **UA-DETRAC dataset** – University at Albany DEtection and TRACking (UA-DETRAC) benchmark dataset. Official project page by Dawei Du: [https://sites.google.com/view/daweidu/projects/ua-detrac](https://sites.google.com/view/daweidu/projects/ua-detrac).  
   - The dataset consists of 100 real-world traffic videos (>140,000 frames) with detailed annotations for multi-object detection and tracking.  

2. **Citation** – Wen, L., Du, D., Cai, Z., Lei, Z., Chang, M.-C., Qi, H., Lim, J., Yang, M.-H., Lyu, S., *UA-DETRAC: A New Benchmark and Protocol for Multi-Object Detection and Tracking*, Computer Vision and Image Understanding (CVIU), 2020.  
   - DOI / journal link if desired: [https://doi.org/10.1016/j.cviu.2019.102907](https://doi.org/10.1016/j.cviu.2019.102907)  

3. **YOLOv8 (Ultralytics)** – Official YOLOv8 documentation for training, model usage, and exporting: [https://docs.ultralytics.com/](https://docs.ultralytics.com/).  

4. **Python libraries used** – OpenCV, Matplotlib, tqdm, etc. (for dataset processing, visualization, and progress tracking).
