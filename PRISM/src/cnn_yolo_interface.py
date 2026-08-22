"""
PRISM Track K -- CNN / YOLOv8 integration interface.

STATUS: PLANNED / NOT TRAINED.

Why not trained this session (real, checked reasons, not a placeholder excuse):
  - No labeled boulder/hazard/ice imagery dataset exists anywhere in this
    project (PROJECT_STATUS.md Section 4, confirmed again this session --
    zero occurrences of YOLOv8/CNN training code or labels anywhere).
  - The one OHRC optical scene physically present locally
    (ch2_ohr_ncp_20251010T0942085687_d_img_d18) was independently confirmed
    NOT to cover the candidate SP_840980_0797630 (PROJECT_STATUS.md Section
    3.4: scene corners are -89.22 to -89.93 deg latitude, a strip within
    ~24 km of the pole; the candidate is ~179 km from the pole). Training or
    running inference "for the candidate" on this scene would describe the
    wrong patch of the Moon.
  - No ground-truth ice/boulder/hazard labels exist for any scene in this
    project (consistent with the task's explicit instruction not to
    fabricate ground-truth labels or claim trained-model accuracy that does
    not exist).

This module defines the INTERFACE a future trained CNN/YOLOv8 model would
need to satisfy to plug into the rest of the PRISM pipeline (feature/evidence
scoring in src/physics_evidence_score.py, demo assembly in
src/build_demo_outputs.py), so that adding a real model later is a matter of
implementing these functions, not redesigning the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


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
    """Interface stub. NOT TRAINED. Calling any method raises NotImplementedError
    with an explanation, rather than returning a fabricated result."""

    STATUS = "PLANNED / NOT TRAINED"

    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = weights_path
        if weights_path is not None:
            raise NotImplementedError(
                "No trained YOLOv8 weights exist in this project. "
                "See module docstring for why (no labeled dataset, no covering OHRC scene)."
            )

    def detect(self, image: np.ndarray, scene_id: str) -> list[BoulderDetection]:
        raise NotImplementedError(
            f"{self.STATUS}. Cannot run detection: no trained model exists. "
            "This method's SIGNATURE is the intended integration point for a future "
            "trained model -- implementing it is out of scope for this session "
            "(no labeled training data, no candidate-covering optical scene)."
        )


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
            "status": "PLANNED / NOT TRAINED",
            "reason": "No labeled boulder/hazard dataset; no candidate-covering optical imagery.",
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
