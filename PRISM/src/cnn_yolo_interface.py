"""
PRISM Track K -- CNN / YOLOv8 integration interface.

STATUS: YOLOv8 TRAINED, diagnostically run on real ShadowCam crops, NOT
production-ready. Real history, not a placeholder:

  - A real YOLOv8n-seg boulder detector now exists (PRISM/models/
    boulder_detector_yolov8n_seg.pt), trained on BoulderNet (Prieur et al.
    2023), filtered to lunar-only imagery. Validated on its own held-out
    test set: box mAP50=0.551, mask mAP50=0.179 (see models/README.md).
  - That model was run for the FIRST time on this project's own real
    ShadowCam PSR crops via src/boulder_detection_shadowcam.py (Tier 0 of
    PRISM/../okay-good-i-want-sparkling-cat.md's enhancement plan). Result,
    honestly: on the dimmest crop (the primary candidate), it produces a
    handful of plausible-looking detections concentrated on the real
    illuminated rim, plus a few likely-spurious low-confidence boxes in the
    genuinely black interior. On brighter shortlist crops, it collapses
    into severe overdetection (200-300+ overlapping false-positive boxes) --
    a real, confirmed domain-transfer failure, not a bug in this interface.
    A quick check ruled out push-broom column striping as the specific
    cause (striping-to-overall-variance ratio is similar in good and bad
    crops); more likely a general low-SNR/texture domain mismatch with the
    sunlit BoulderNet training distribution.
  - See PRISM/outputs/objective_optical/boulder_detection/
    raw_inference_summary.json for the full per-crop, per-threshold record.
  - The original OHRC scene (ch2_ohr_ncp_20251010T0942085687_d_img_d18) is
    still confirmed not to cover the candidate -- irrelevant now that real
    ShadowCam coverage exists (see docs/CANDIDATE_ACQUISITION_SELECTION.md).

This module wires Yolov8BoulderDetector to the real trained model. It is
explicitly NOT a validated production detector for this domain -- no
ground-truth boulders exist for any PSR interior anywhere to confirm
against, and the raw-crop overdetection failure above is real and
unresolved pending Tier 1/2 of the enhancement plan.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional
import numpy as np

_DEFAULT_WEIGHTS = os.path.join(os.path.dirname(__file__), "..", "models", "boulder_detector_yolov8n_seg.pt")


@dataclass
class BoulderDetection:
    """One detected object, in image-pixel coordinates of the source OHRC/TMC scene."""
    bbox_px: tuple  # (x_min, y_min, x_max, y_max)
    confidence: float
    class_label: str  # e.g. "boulder", "shadow", "crater_rim"


@dataclass
class CnnHazardMap:
    """Per-pixel hazard/anomaly probability map, same grid as the source optical scene."""
    probability_map: np.ndarray  # float32, [0, 1], shape (H, W)
    source_scene_id: str
    model_version: Optional[str] = None


class Yolov8BoulderDetector:
    """Wraps the real trained YOLOv8n-seg boulder detector. TRAINED but NOT
    validated for this domain -- see module docstring for the real
    overdetection failure found when run on this project's own ShadowCam
    crops. Callers should treat detect() output as diagnostic, not
    production-quality, until Tier 1/2 of the enhancement plan improve on
    the raw-crop result."""

    STATUS = "TRAINED, diagnostic-only for real ShadowCam domain"

    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = weights_path or _DEFAULT_WEIGHTS
        if not os.path.exists(self.weights_path):
            raise FileNotFoundError(
                f"No weights found at {self.weights_path}. Train first "
                "(see PRISM/models/README.md) or pass an explicit weights_path."
            )
        from ultralytics import YOLO  # local import: keep this module importable without ultralytics installed
        self._model = YOLO(self.weights_path)

    def detect(self, image: np.ndarray, scene_id: str, conf: float = 0.10, iou: float = 0.45) -> list[BoulderDetection]:
        results = self._model.predict(image, conf=conf, iou=iou, verbose=False)
        r = results[0]
        detections = []
        if r.boxes is not None:
            for box, confidence in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist()):
                detections.append(BoulderDetection(
                    bbox_px=tuple(box),
                    confidence=float(confidence),
                    class_label="boulder",
                ))
        return detections


class CnnAnomalyClassifier:
    """Interface stub for a future CNN-based optical hazard/anomaly classifier.
    NOT TRAINED -- see module docstring."""

    STATUS = "PLANNED / NOT TRAINED"

    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = weights_path
        if weights_path is not None:
            raise NotImplementedError(
                "No trained CNN weights exist in this project. "
                "No ground-truth ice/hazard labels exist to train one, per task instruction "
                "not to fabricate labels."
            )

    def predict(self, image: np.ndarray, scene_id: str) -> CnnHazardMap:
        raise NotImplementedError(
            f"{self.STATUS}. Cannot run inference: no trained model exists."
        )


def integration_status() -> dict:
    """Machine-readable status for the demo/report layer -- call this instead
    of trying to run detect()/predict() when just reporting pipeline status."""
    return {
        "yolov8": {
            "status": "TRAINED, diagnostic-only for real ShadowCam domain",
            "weights": "PRISM/models/boulder_detector_yolov8n_seg.pt",
            "validated_metrics_on_own_test_set": {"box_mAP50": 0.551, "mask_mAP50": 0.179},
            "real_shadowcam_diagnostic": (
                "Run on all 13 real ShadowCam crops (src/boulder_detection_shadowcam.py). "
                "Dimmest crop (primary candidate): sparse, plausible detections on the real "
                "illuminated rim. Brighter crops: severe overdetection (200-300+ false "
                "positives), a real confirmed domain-transfer failure, not yet resolved. "
                "See PRISM/outputs/objective_optical/boulder_detection/raw_inference_summary.json."
            ),
            "reason_not_production_ready": "No ground-truth boulders exist for any PSR interior to validate against; raw-crop overdetection unresolved pending image-enhancement work.",
        },
        "cnn": {
            "status": "PLANNED / NOT TRAINED",
            "reason": "No ground-truth ice/hazard labels exist anywhere in this project.",
        },
        "integration_interface": "src/cnn_yolo_interface.py -- Yolov8BoulderDetector, CnnAnomalyClassifier, BoulderDetection, CnnHazardMap",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(integration_status(), indent=2))
