
# YOLOv5 Model Validation Report

**Date:** 2026-04-07 21:02:22
**Model:** models/yolov5_1k.pt
**Dataset:** vehicle_dataset/data.yaml

---

## 1. Overall Performance Metrics

| Metric       | Value  |
|--------------|--------|
| mAP@.5-.95   | 0.8777  |
| mAP@.5       | 0.9806  |
| Precision    | 0.9765  |
| Recall       | 0.9594  |

---

## 2. Analysis & Interpretation

**Precision-Recall Balance:**
The PR curve and F1 score give insight into the trade-off between precision and recall. A high area under the PR curve indicates good performance across all confidence thresholds.

**Overfitting/Underfitting Check:**
- Compare these validation metrics with your training metrics.
- If training mAP is significantly higher than validation mAP, the model is likely **overfitting**.
- If both are low, the model may be **underfitting**.
- If they are close and reasonably high, the model is generalizing well.

**Error Analysis from Confusion Matrix:**
- The confusion matrix (visualized above) shows which classes are being confused for others.
- The 'background' class in the matrix represents false positives (detections that don't match any ground truth) and false negatives (ground truth objects that were missed).

---

## 3. Recommendations

- **If Overfitting:** Consider adding more diverse training data, increasing data augmentation, or using a smaller model.
- **If Underfitting:** Consider training for more epochs, using a larger model, or ensuring your dataset is representative.
- **If there are many False Positives:** Try increasing the confidence threshold (`conf`).
- **If there are many False Negatives:** Try lowering the confidence threshold (`conf`).

---

**Validation artifacts are saved in:** F:\projects\object-detection-for-traffic-using-yolo\runs\detect\validation_results\yolo_validation
