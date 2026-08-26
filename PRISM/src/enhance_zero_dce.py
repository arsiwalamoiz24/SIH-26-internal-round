"""
Tier 1: Zero-DCE-style low-light enhancement, self-supervised PER CROP
(the "zero-reference" variant -- no paired training data needed, no
external pretrained checkpoint of unknown provenance either).

IMPORTANT PROVENANCE NOTE, disclosed in every output: this is a general
perceptual low-light curve estimator, NOT built on a sensor physical noise
model like HORUS. Output pixel values carry NO radiometric meaning and are
NOT a claim of recovered physical signal -- this is an unvalidated
engineering enhancement experiment, never to be described as a "denoiser"
or "signal recovery" method. It is a real, evidenced technique (Zero-DCE,
Guo et al. 2020 CVPR) but a categorically different, weaker scientific
claim than Tier 2's physics-grounded approach.

Architecture: lightweight 7-conv-layer curve-estimation network (DCE-Net),
iteratively applies a per-pixel quadratic enhancement curve. Losses:
spatial consistency (preserve local structure), exposure control (push
local mean brightness toward a target), illumination smoothness (smooth
curve maps). Color constancy loss from the original paper is DROPPED here
since the input is single-band calibrated radiance replicated to 3
channels for the detector, not true RGB -- there is no real color
information to correct, and applying a color-constancy loss to a
replicated-grayscale image would be meaningless, not a genuine adaptation
of the method.
"""
import json
import os

import numpy as np
import rasterio
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
N_ITER = 8  # curve application iterations, as in the original Zero-DCE
NODATA_SENTINEL = -1e30


class DCENet(nn.Module):
    def __init__(self, n_iter=N_ITER):
        super().__init__()
        self.n_iter = n_iter
        ch = 32
        self.e_conv1 = nn.Conv2d(3, ch, 3, 1, 1)
        self.e_conv2 = nn.Conv2d(ch, ch, 3, 1, 1)
        self.e_conv3 = nn.Conv2d(ch, ch, 3, 1, 1)
        self.e_conv4 = nn.Conv2d(ch, ch, 3, 1, 1)
        self.e_conv5 = nn.Conv2d(ch * 2, ch, 3, 1, 1)
        self.e_conv6 = nn.Conv2d(ch * 2, ch, 3, 1, 1)
        self.e_conv7 = nn.Conv2d(ch * 2, 3 * n_iter, 3, 1, 1)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x1 = self.relu(self.e_conv1(x))
        x2 = self.relu(self.e_conv2(x1))
        x3 = self.relu(self.e_conv3(x2))
        x4 = self.relu(self.e_conv4(x3))
        x5 = self.relu(self.e_conv5(torch.cat([x3, x4], 1)))
        x6 = self.relu(self.e_conv6(torch.cat([x2, x5], 1)))
        curves = torch.tanh(self.e_conv7(torch.cat([x1, x6], 1)))
        curve_maps = torch.split(curves, 3, dim=1)  # n_iter tensors of shape (B,3,H,W)

        enhanced = x
        for c in curve_maps:
            enhanced = enhanced + c * (enhanced.pow(2) - enhanced)
        return enhanced, curve_maps


def spatial_consistency_loss(enhanced, original):
    kernels = {
        "left": torch.tensor([[0, 0, 0], [-1, 1, 0], [0, 0, 0]], dtype=torch.float32),
        "right": torch.tensor([[0, 0, 0], [0, 1, -1], [0, 0, 0]], dtype=torch.float32),
        "up": torch.tensor([[0, -1, 0], [0, 1, 0], [0, 0, 0]], dtype=torch.float32),
        "down": torch.tensor([[0, 0, 0], [0, 1, 0], [0, -1, 0]], dtype=torch.float32),
    }
    orig_mean = original.mean(dim=1, keepdim=True)
    enh_mean = enhanced.mean(dim=1, keepdim=True)
    orig_pool = F.avg_pool2d(orig_mean, 4)
    enh_pool = F.avg_pool2d(enh_mean, 4)
    loss = 0.0
    for k in kernels.values():
        k = k.view(1, 1, 3, 3).to(original.device)
        d_orig = F.conv2d(orig_pool, k, padding=1)
        d_enh = F.conv2d(enh_pool, k, padding=1)
        loss = loss + (d_orig - d_enh).pow(2).mean()
    return loss


def exposure_control_loss(enhanced, target_exposure=0.35, patch_size=16):
    mean_channels = enhanced.mean(dim=1, keepdim=True)
    pooled = F.avg_pool2d(mean_channels, patch_size)
    return (pooled - target_exposure).pow(2).mean()


def illumination_smoothness_loss(curve_maps):
    loss = 0.0
    for c in curve_maps:
        dh = (c[:, :, 1:, :] - c[:, :, :-1, :]).pow(2).mean()
        dw = (c[:, :, :, 1:] - c[:, :, :, :-1]).pow(2).mean()
        loss = loss + dh + dw
    return loss / len(curve_maps)


def output_smoothness_loss(enhanced):
    """Direct total-variation regularization on the OUTPUT image (not just
    the curve maps) -- the curve-map smoothness term alone was insufficient
    to stop per-pixel noise amplification in early testing (real finding:
    adjacent-pixel correlation on the primary candidate crop collapsed from
    0.994 in the raw radiance to 0.262 after enhancement -- structure was
    being replaced with grain, not just smoothing lost detail)."""
    dh = (enhanced[:, :, 1:, :] - enhanced[:, :, :-1, :]).abs().mean()
    dw = (enhanced[:, :, :, 1:] - enhanced[:, :, :, :-1]).abs().mean()
    return dh + dw


def find_crops():
    crops = ["PRISM/outputs/objective_optical/SP_840980_0797630_shadowcam_crop.tif"]
    shortlist_dir = "PRISM/outputs/objective_optical/shortlist_shadowcam"
    for f in sorted(os.listdir(shortlist_dir)):
        if f.endswith(".tif"):
            crops.append(os.path.join(shortlist_dir, f))
    return crops


def enhance_crop(data, n_steps=300, lr=1e-3):
    valid = data > NODATA_SENTINEL
    valid_vals = data[valid]
    lo, hi = np.percentile(valid_vals, [1, 99])
    norm = np.clip((data - lo) / (hi - lo + 1e-12), 0, 1)
    norm[~valid] = 0

    x = torch.from_numpy(norm).float().unsqueeze(0).unsqueeze(0).repeat(1, 3, 1, 1).to(DEVICE)

    model = DCENet().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    for step in range(n_steps):
        opt.zero_grad()
        enhanced, curves = model(x)
        loss = (
            20.0 * spatial_consistency_loss(enhanced, x)
            + 3.0 * exposure_control_loss(enhanced)
            + 200.0 * illumination_smoothness_loss(curves)
            + 15.0 * output_smoothness_loss(enhanced)
        )
        loss.backward()
        opt.step()

    with torch.no_grad():
        enhanced, _ = model(x)
    enhanced_np = enhanced.squeeze(0).mean(dim=0).cpu().numpy()  # collapse replicated channels
    enhanced_np[~valid] = 0
    return enhanced_np, float(loss.item())


def main():
    out_dir = "PRISM/outputs/objective_optical/boulder_detection/zero_dce_enhanced"
    os.makedirs(out_dir, exist_ok=True)
    crops = find_crops()
    print(f"Device: {DEVICE}. Enhancing {len(crops)} real crops (self-supervised, ~300 steps each)...")

    summary = {}
    for crop_path in crops:
        crop_id = os.path.splitext(os.path.basename(crop_path))[0]
        with rasterio.open(crop_path) as ds:
            data = ds.read(1).astype(np.float64)
            profile = ds.profile

        enhanced, final_loss = enhance_crop(data)

        out_tif = os.path.join(out_dir, f"{crop_id}_zerodce.tif")
        profile.update(dtype="float32", count=1)
        with rasterio.open(out_tif, "w", **profile) as dst:
            dst.write(enhanced.astype(np.float32), 1)

        img8 = (np.clip(enhanced, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(img8).save(os.path.join(out_dir, f"{crop_id}_zerodce.png"))

        print(f"{crop_id}: final_loss={final_loss:.5f}")
        summary[crop_id] = {"final_loss": final_loss, "output_tif": out_tif}

    out_summary = {
        "source_type": "DERIVED",
        "scientific_validity": (
            "Unvalidated engineering enhancement -- Zero-DCE-style self-supervised "
            "curve estimation, a general perceptual low-light enhancer, NOT built "
            "on a sensor noise model. Output pixel values carry no radiometric "
            "meaning and are not a claim of recovered physical signal. Real and "
            "evidenced as a technique (Guo et al. 2020, CVPR) but categorically "
            "weaker than a physics-grounded denoiser -- never call this a "
            "'denoiser' or 'signal recovery' method."
        ),
        "method": "Self-supervised per-crop DCE-Net (7-conv curve estimator, 8 iterations), "
                  "spatial-consistency + exposure-control + illumination-smoothness losses. "
                  "Color-constancy loss from the original paper dropped (input is single-band "
                  "radiance replicated to 3 channels, not true RGB -- no real color to correct).",
        "crops": summary,
    }
    with open(os.path.join(out_dir, "zero_dce_summary.json"), "w") as f:
        json.dump(out_summary, f, indent=2)
    print(f"\nDone. Summary: {out_dir}/zero_dce_summary.json")


if __name__ == "__main__":
    main()
