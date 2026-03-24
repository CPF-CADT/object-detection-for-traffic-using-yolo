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

## Installation
1. Clone the repo: `git clone https://github.com/yourusername/your-repo-name.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Download and extract UA-DETRAC dataset as described above.

## Usage
1. Run the preprocessing notebook: Open `data_preprocessing.ipynb` in Jupyter and execute all cells.
2. This creates a `vehicle_dataset/` folder with YOLO-formatted data.
3. Train YOLO: Use Ultralytics YOLOv8 (e.g., `yolo train data=vehicle_dataset/data.yaml model=yolov8n.pt`).

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies.

## Results
- Processed ~13,795 images across train/val/test.
- All annotations in YOLO format with class 0 (vehicle).

## License
MIT License (or specify your license).