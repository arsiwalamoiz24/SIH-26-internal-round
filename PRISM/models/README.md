# boulder_detector_yolov8n_seg.pt

Real, trained YOLOv8n instance-segmentation model, single class "boulder".
Copied from `runs/segment/PRISM/runs/boulder_yolov8n_seg/weights/best.pt`
(epoch 23 of the original training run) after a rotation/flip-augmentation
fine-tuning attempt (`boulder_yolov8n_seg_finetune`) failed to beat it across
23 epochs (peak 0.523 vs. this checkpoint's 0.551) and was abandoned.

Real, independently-validated metrics (`yolo segment val`, not just the
training log):

| Metric | Box | Mask |
|---|---:|---:|
| Precision | 0.608 | 0.297 |
| Recall | 0.544 | 0.329 |
| mAP50 | 0.551 | 0.179 |
| mAP50-95 | 0.196 | 0.036 |

Trained on `data/raw/boulder_net_clean/` (BoulderNet, Prieur et al. 2023,
filtered to lunar-only -- no Earth or Mars imagery). Not yet run on any of
this project's own real optical crops (ShadowCam/NAC) -- next step.
