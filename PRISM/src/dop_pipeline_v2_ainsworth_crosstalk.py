"""
PRISM -- DOP pipeline v2, Ainsworth et al. 2006 crosstalk/channel-imbalance
calibration, implemented from the actual paper (obtained via the user's IEEE
subscription this session):

    T. L. Ainsworth, L. Ferro-Famil, J.-S. Lee, "Orientation Angle Preserving
    A Posteriori Polarimetric SAR Calibration," IEEE TGRS 44(4):994-1003, 2006.

This supersedes the self-derived reflection-symmetry approximation in
dop_pipeline_v2_crosstalk_correction.py (which assumed A=B=0, i.e. zero
co-pol/cross-pol correlation -- Ainsworth's method explicitly does NOT make
that assumption; it estimates A, B from the data itself).

MODEL (paper Eq. 1-4). Observed scattering vector O = M(k,alpha,u,v,w,z) @ S.
k (relative HH/VV co-pol gain) is fixed to 1 throughout, matching the paper's
own default: k is provably indeterminate from reciprocity alone (Section V),
which is also why relative-HH/VV-gain calibration was already found inert as
a separate hypothesis this session (dop_pipeline_v2_relative_gain_test.py).
With k=1, the forward model is a 4x4 matrix in alpha (cross-pol channel
imbalance) and u,v,w,z (crosstalk), order [HH,HV,VH,VV]:

    O = diag(1/alpha, alpha, 1/alpha, alpha) @ T(u,v,w,z) @ S      [inverse dir]
    T(u,v,w,z) = [[1,v,w,vw],[z,1,wz,w],[u,uv,1,v],[uz,u,z,1]]

TARGET FORM (paper Eq. 8). Calibrated covariance must satisfy reciprocity:
Sigma_HVHV = Sigma_VHVH (=beta), Sigma_HVVH = Sigma_VHHV (=beta', real),
plus two data-estimated complex parameters A = Sigma_HVHH = Sigma_VHHH and
B = Sigma_HVVV = Sigma_VHVV (NOT assumed zero -- this is what distinguishes
Ainsworth's method from the cruder reflection-symmetry attempt already ruled
out).

ITERATION (paper Section IV, the numbered procedure, all 6 steps legible in
the extracted text and implemented verbatim below):
  1) alpha0 from raw covariance C (Eq. 13), crosstalk=0.
  2) apply alpha to C -> Sigma' (Eq. 10/11).
  3) estimate A, B from Sigma' (Eq. 12).
  4) solve linearized crosstalk equations for u,v,w,z -> apply exact inverse
     crosstalk matrix (Eq. 16) to get Sigma''.
  5) recompute alpha'' from Sigma'' (Eq. 20), alpha_total *= alpha''.
  6) rescale v,z by alpha''^2 (Eq. 21), loop to step 2. ~6 iterations to converge.

IMPLEMENTATION NOTE ON THE CROSSTALK LINEAR SYSTEM: the paper's own
intermediate matrices ([zeta],[tau], Eq. 17-19) were corrupted by PDF text
extraction (a 4x4 matrix scrambled into an unparseable fragment) and could
not be transcribed reliably. Rather than guess at corrupted equations, the
four complex linearized constraint equations were RE-DERIVED here directly
from the paper's own clean, legible statements: the forward model (Eq. 1-4)
and the target covariance form (Eq. 8), via first-order (T = I+N) expansion
of Sigma' ~= (I+N) Sigma_target (I+N)^dagger. This derivation independently
reproduces the one intermediate equation that IS legible in the extracted
text ("A = Sigma''_HVHH ~= Sigma'_HVHH - w*Sigma'_VVHH - z*Sigma'_HHHH -
v* Sigma'_HVHV - w* Sigma'_HVVH + ...") confirming the derivation is
consistent with the paper, and is documented in full in the project's plan
file (graceful-wandering-wand.md) for audit.

KNOWN DEFECT (Xing, Dai, Liu, Wang, "Comment on 'Orientation Angle
Preserving...'," IEEE TGRS 50(6):2417-2419, 2012 -- also read via IEEE this
session): Ainsworth's own Eq. (15) has the calibration matrix multiplication
order reversed relative to its derivation (should be Eq. 16's order). This
forces the recovered crosstalk estimates toward v~=-w*alpha^2, u~=-z*alpha^2,
which Xing's own simulation shows can differ substantially from the true
values (their Table I). This implementation reproduces Ainsworth's algorithm
AS PUBLISHED (matching the user's explicit choice to implement "the actual
Ainsworth 2006 algorithm," and matching what Zhao et al. 2024 -- PRISM's
own DFSAR calibration reference -- cites and uses as their "Ans" method) and
reports this caveat in the output rather than silently patching it with
Xing's proposed fix.

Reuses the same real, already-downloaded acquisition, bias constants, and
F2/F3 crater window/mask geometry as the other v2 scripts. Does not modify
or delete any v1 or other v2 script/output.
"""

import json
import os
import time

import numpy as np
from scipy.ndimage import uniform_filter
import rasterio
from rasterio.windows import Window
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop_v2")
os.makedirs(OUT_DIR, exist_ok=True)

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20200321t082617351_d_fp_d18.zip"
INTERNAL_DIR = "data/calibrated/20200321"
BASE = "ch2_sar_ncxl_20200321t082617351_d_sli_xx_fp"
STATION = "d18"
TOTAL_SAMPLES = 512
TOTAL_LINES = 343723
LINE_SPACING_M = 0.488885
PIXEL_SPACING_M = 9.593359

BIAS = {
    "HH": (1.383863, -2.668324), "HV": (-5.628389, -0.892712),
    "VH": (6.038121, -8.525171), "VV": (-1.53899, -1.015972),
}

CRATERS = [
    {"id": "F2", "diameter_m": 1100, "center_line": 47719, "center_sample": 112, "context_half_m": 2000},
    {"id": "F3", "diameter_m": 700, "center_line": 59527, "center_sample": 29, "context_half_m": 1300},
]
PAPER_RANGE = [0.10, 0.13]
POLS = ["HH", "HV", "VH", "VV"]  # fixed index order 0,1,2,3 throughout
N_ITER = 8


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol.lower()}_{STATION}.tif"


def read_complex_window(pol, line_start, line_count):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, TOTAL_SAMPLES, line_count)
        real = src.read(1, window=window).astype(np.float32)
        imag = src.read(2, window=window).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


def build_covariance(S):
    """S: dict pol -> 1D complex array (same length, already masked to interior).
    Returns 4x4 complex covariance matrix, C[i,j] = mean(S_i * conj(S_j)), order POLS."""
    C = np.zeros((4, 4), dtype=complex)
    for i, pi in enumerate(POLS):
        for j, pj in enumerate(POLS):
            C[i, j] = np.mean(S[pi] * np.conj(S[pj]))
    return C


def apply_alpha_to_covariance(C, alpha):
    """Sigma' = diag(g) C diag(g)^H, g = [1/alpha, alpha, 1/alpha, alpha] (k=1). Eq. 10/11."""
    g = np.array([1.0 / alpha, alpha, 1.0 / alpha, alpha], dtype=complex)
    return np.outer(g, np.conj(g)) * C


def estimate_alpha(C):
    """Eq. 13: alpha = |C_VHVH/C_HVHV|^(1/4) * exp(i*angle(C_VHHV)/2)."""
    i_hh, i_hv, i_vh, i_vv = 0, 1, 2, 3
    c_hvhv = C[i_hv, i_hv]
    c_vhvh = C[i_vh, i_vh]
    c_vhhv = C[i_vh, i_hv]
    mag = np.abs(c_vhvh / c_hvhv) ** 0.25
    phase = np.angle(c_vhhv) / 2.0
    return mag * np.exp(1j * phase)


def solve_crosstalk(Sigma_p, A, B):
    """Solve the 4 complex (8 real) linearized equations for u,v,w,z, derived
    from Sigma' ~= (I+N) Sigma_target (I+N)^dagger, N the first-order crosstalk
    perturbation matrix -- see module docstring. Order: HH=0,HV=1,VH=2,VV=3.
    """
    i_hh, i_hv, i_vh, i_vv = 0, 1, 2, 3
    Shhhh = Sigma_p[i_hh, i_hh]
    Svvhh = Sigma_p[i_vv, i_hh]
    Shhvv = Sigma_p[i_hh, i_vv]
    Svvvv = Sigma_p[i_vv, i_vv]
    beta = Sigma_p[i_hv, i_hv]      # Sigma_HVHV
    beta_p = Sigma_p[i_hv, i_vh]    # Sigma_HVVH (beta')
    rhs1 = Sigma_p[i_hv, i_hh] - A  # Eq I
    rhs2 = Sigma_p[i_vh, i_hh] - A  # Eq II
    rhs3 = Sigma_p[i_hv, i_vv] - B  # Eq III
    rhs4 = Sigma_p[i_vh, i_vv] - B  # Eq IV

    # unknowns real vector: [Re(u),Im(u),Re(v),Im(v),Re(w),Im(w),Re(z),Im(z)]
    idx = {"u": 0, "v": 2, "w": 4, "z": 6}

    def add_term(row_re, row_im, var, coeff, conj):
        b = idx[var]
        cr, ci = coeff.real, coeff.imag
        if not conj:
            # coeff * x contributes: Re: cr*Rex - ci*Imx ; Im: ci*Rex + cr*Imx
            row_re[b] += cr; row_re[b + 1] += -ci
            row_im[b] += ci; row_im[b + 1] += cr
        else:
            # coeff * conj(x) contributes: Re: cr*Rex + ci*Imx ; Im: ci*Rex - cr*Imx
            row_re[b] += cr; row_re[b + 1] += ci
            row_im[b] += ci; row_im[b + 1] += -cr

    Mat = np.zeros((8, 8))
    rhs = np.zeros(8)

    # Eq I: v*conj(beta) ... wait coefficients multiply the unknown; here the
    # unknown is v and its coefficient is beta, appearing as beta*conj(v):
    # Sigma'_HVHH ~= A + z*Shhhh + w*Svvhh + beta*conj(v) + beta_p*conj(w)
    r_re = np.zeros(8); r_im = np.zeros(8)
    add_term(r_re, r_im, "z", Shhhh, conj=False)
    add_term(r_re, r_im, "w", Svvhh, conj=False)
    add_term(r_re, r_im, "v", beta, conj=True)
    add_term(r_re, r_im, "w", beta_p, conj=True)
    Mat[0, :] = r_re; Mat[1, :] = r_im
    rhs[0] = rhs1.real; rhs[1] = rhs1.imag

    # Eq II: Sigma'_VHHH ~= A + u*Shhhh + v*Svvhh + beta_p*conj(v) + beta*conj(w)
    r_re = np.zeros(8); r_im = np.zeros(8)
    add_term(r_re, r_im, "u", Shhhh, conj=False)
    add_term(r_re, r_im, "v", Svvhh, conj=False)
    add_term(r_re, r_im, "v", beta_p, conj=True)
    add_term(r_re, r_im, "w", beta, conj=True)
    Mat[2, :] = r_re; Mat[3, :] = r_im
    rhs[2] = rhs2.real; rhs[3] = rhs2.imag

    # Eq III: Sigma'_HVVV ~= B + z*Shhvv + w*Svvvv + beta*conj(u) + beta_p*conj(z)
    r_re = np.zeros(8); r_im = np.zeros(8)
    add_term(r_re, r_im, "z", Shhvv, conj=False)
    add_term(r_re, r_im, "w", Svvvv, conj=False)
    add_term(r_re, r_im, "u", beta, conj=True)
    add_term(r_re, r_im, "z", beta_p, conj=True)
    Mat[4, :] = r_re; Mat[5, :] = r_im
    rhs[4] = rhs3.real; rhs[5] = rhs3.imag

    # Eq IV: Sigma'_VHVV ~= B + u*Shhvv + v*Svvvv + beta_p*conj(u) + beta*conj(z)
    r_re = np.zeros(8); r_im = np.zeros(8)
    add_term(r_re, r_im, "u", Shhvv, conj=False)
    add_term(r_re, r_im, "v", Svvvv, conj=False)
    add_term(r_re, r_im, "u", beta_p, conj=True)
    add_term(r_re, r_im, "z", beta, conj=True)
    Mat[6, :] = r_re; Mat[7, :] = r_im
    rhs[6] = rhs4.real; rhs[7] = rhs4.imag

    sol = np.linalg.solve(Mat, rhs)
    u = sol[0] + 1j * sol[1]
    v = sol[2] + 1j * sol[3]
    w = sol[4] + 1j * sol[5]
    z = sol[6] + 1j * sol[7]
    return u, v, w, z


def crosstalk_matrix(u, v, w, z):
    return np.array([
        [1, v, w, v * w],
        [z, 1, w * z, w],
        [u, u * v, 1, v],
        [u * z, u, z, 1],
    ], dtype=complex)


def crosstalk_inverse(u, v, w, z):
    """Closed form, Eq. 16."""
    scale = 1.0 / ((1 - v * z) * (1 - u * w))
    return scale * np.array([
        [1, -v, -w, v * w],
        [-z, 1, w * z, -w],
        [-u, u * v, 1, -v],
        [u * z, -u, -z, 1],
    ], dtype=complex)


def ainsworth_calibrate(C, n_iter=N_ITER, verbose=True, label=""):
    """Full iteration per paper Section IV steps 1-6. Returns dict of final
    parameters + per-iteration history + validity diagnostics."""
    alpha_total = estimate_alpha(C)
    u = v = w = z = 0j
    history = []

    for it in range(n_iter):
        Sigma_p = apply_alpha_to_covariance(C, alpha_total)          # step 2
        i_hh, i_hv, i_vh, i_vv = 0, 1, 2, 3
        A = (Sigma_p[i_hv, i_hh] + Sigma_p[i_vh, i_hh]) / 2.0         # step 3
        B = (Sigma_p[i_hv, i_vv] + Sigma_p[i_vh, i_vv]) / 2.0

        u, v, w, z = solve_crosstalk(Sigma_p, A, B)                   # step 4
        Tinv = crosstalk_inverse(u, v, w, z)
        Sigma_pp = Tinv @ Sigma_p @ Tinv.conj().T

        alpha_pp = estimate_alpha(Sigma_pp)                           # step 5
        alpha_total = alpha_total * alpha_pp

        v = v / (alpha_pp ** 2)                                       # step 6
        z = z * (alpha_pp ** 2)

        beta = Sigma_pp[i_hv, i_hv]
        beta_p = Sigma_pp[i_hv, i_vh]
        eta = beta - beta_p
        rec = {
            "iter": it, "alpha_total": [alpha_total.real, alpha_total.imag],
            "alpha_pp": [alpha_pp.real, alpha_pp.imag],
            "u": [u.real, u.imag], "v": [v.real, v.imag],
            "w": [w.real, w.imag], "z": [z.real, z.imag],
            "abs_u": float(abs(u)), "abs_v": float(abs(v)),
            "abs_w": float(abs(w)), "abs_z": float(abs(z)),
            "eta": [float(eta.real), float(eta.imag)],
            "eta_over_beta": float((eta / beta).real) if beta != 0 else None,
        }
        history.append(rec)
        if verbose:
            print(f"  [{label}] iter {it}: |u|={rec['abs_u']:.4f} |v|={rec['abs_v']:.4f} "
                  f"|w|={rec['abs_w']:.4f} |z|={rec['abs_z']:.4f} "
                  f"|alpha|={abs(alpha_total):.4f} eta/beta={rec['eta_over_beta']}")

    max_mag = max(abs(u), abs(v), abs(w), abs(z))
    return {
        "alpha_final": [alpha_total.real, alpha_total.imag],
        "u": [u.real, u.imag], "v": [v.real, v.imag],
        "w": [w.real, w.imag], "z": [z.real, z.imag],
        "max_crosstalk_magnitude": float(max_mag),
        "linearization_valid": bool(max_mag < 1.0),
        "history": history,
        "final_eta_over_beta": history[-1]["eta_over_beta"],
        "positive_definite_concern": bool(history[-1]["eta_over_beta"] is not None and history[-1]["eta_over_beta"] > 1.0),
    }, alpha_total, u, v, w, z


def calibrate_pixels(raw, alpha, u, v, w, z):
    """Apply final calibration to per-pixel arrays. raw: dict pol -> 2D complex
    array (bias-centered only). Mirrors the covariance-domain order: alpha
    first, then crosstalk inverse (matching steps 2 then 4 above)."""
    g = {"HH": 1.0 / alpha, "HV": alpha, "VH": 1.0 / alpha, "VV": alpha}
    Op = {p: raw[p] * g[p] for p in POLS}
    Tinv = crosstalk_inverse(u, v, w, z)
    shape = raw["HH"].shape
    stacked = np.stack([Op[p].ravel() for p in POLS], axis=0)  # 4 x N
    calibrated = Tinv @ stacked
    out = {p: calibrated[i].reshape(shape) for i, p in enumerate(POLS)}
    return out


def stokes_dop(A, B, window_size):
    PA = uniform_filter(np.abs(A) ** 2, size=window_size, mode="reflect")
    PB = uniform_filter(np.abs(B) ** 2, size=window_size, mode="reflect")
    cross = A * np.conj(B)
    Re_AB = uniform_filter(cross.real, size=window_size, mode="reflect")
    Im_AB = uniform_filter(cross.imag, size=window_size, mode="reflect")
    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * Re_AB
    S4 = -2 * Im_AB
    with np.errstate(divide="ignore", invalid="ignore"):
        dop = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
    return dop


def aggregate_dop(A, B, mask):
    a = A[mask]; b = B[mask]
    PA = np.mean(np.abs(a) ** 2); PB = np.mean(np.abs(b) ** 2)
    cross = np.mean(a * np.conj(b))
    S1 = PA + PB; S2 = PA - PB; S3 = 2 * cross.real; S4 = -2 * cross.imag
    return np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1


def main():
    t0 = time.time()
    results = {}
    for crater in CRATERS:
        cid = crater["id"]
        print(f"\n=== {cid} ===")
        half_lines_ctx = int(crater["context_half_m"] / LINE_SPACING_M)
        line_start = max(0, crater["center_line"] - half_lines_ctx)
        line_count = min(2 * half_lines_ctx, TOTAL_LINES - line_start)

        raw = {}
        for pol in POLS:
            arr = read_complex_window(pol, line_start, line_count) - complex(*BIAS[pol])
            raw[pol] = arr

        local_center_line = crater["center_line"] - line_start
        local_center_sample = crater["center_sample"]
        radius_m = crater["diameter_m"] / 2.0
        rows_idx, cols_idx = np.indices(raw["HH"].shape)
        dist_m = np.hypot((rows_idx - local_center_line) * LINE_SPACING_M,
                           (cols_idx - local_center_sample) * PIXEL_SPACING_M)
        mask = dist_m <= radius_m

        S_interior = {p: raw[p][mask] for p in POLS}
        C = build_covariance(S_interior)

        cal_params, alpha, u, v, w, z = ainsworth_calibrate(C, label=cid)
        print(f"  FINAL: alpha={alpha:.4f} u={u:.4f} v={v:.4f} w={w:.4f} z={z:.4f} "
              f"max|crosstalk|={cal_params['max_crosstalk_magnitude']:.4f} "
              f"linearization_valid={cal_params['linearization_valid']}")

        calibrated = calibrate_pixels(raw, alpha, u, v, w, z)
        HH_cal, VV_cal = calibrated["HH"], calibrated["VV"]
        HH_raw, VV_raw = raw["HH"], raw["VV"]

        dop_agg_before = aggregate_dop(HH_raw, VV_raw, mask)
        dop_agg_after = aggregate_dop(HH_cal, VV_cal, mask)

        table = []
        for ws in [5, 9, 15, 21, 31, 41]:
            dop_before = stokes_dop(HH_raw, VV_raw, ws)
            dop_after = stokes_dop(HH_cal, VV_cal, ws)
            vb = dop_before[mask]; vb = vb[np.isfinite(vb)]
            va = dop_after[mask]; va = va[np.isfinite(va)]
            table.append({
                "window_size_px": ws,
                "dop_mean_before": float(vb.mean()),
                "dop_mean_after_ainsworth": float(va.mean()),
                "meets_paper_range_after": bool(PAPER_RANGE[0] <= va.mean() <= PAPER_RANGE[1]),
            })
            print(f"  ws={ws:2d}  before={vb.mean():.4f}  after(Ainsworth)={va.mean():.4f}")

        result = {
            "crater_id": cid,
            "n_interior_px": int(mask.sum()),
            "calibration_params": cal_params,
            "aggregate_whole_interior_dop": {
                "before": float(dop_agg_before), "after_ainsworth": float(dop_agg_after),
                "meets_paper_range": bool(PAPER_RANGE[0] <= dop_agg_after <= PAPER_RANGE[1]),
            },
            "windowed_table": table,
            "paper_range": PAPER_RANGE,
            "xing_2012_caveat": (
                "Ainsworth's published Eq.15 has a matrix-multiplication-order bug "
                "(Xing et al. 2012 comment, IEEE TGRS 50(6):2417-2419) that forces "
                "v~=-w*alpha^2, u~=-z*alpha^2 in the recovered crosstalk estimates -- "
                "this run reproduces Ainsworth's algorithm AS PUBLISHED, not Xing's "
                "proposed fix. Check whether the printed u,v,w,z satisfy that relation."
            ),
        }
        results[cid] = result
        print(f"  AGGREGATE DOP: before={dop_agg_before:.4f}  after(Ainsworth)={dop_agg_after:.4f}  "
              f"(paper: {PAPER_RANGE})  meets_range={result['aggregate_whole_interior_dop']['meets_paper_range']}")

    with open(os.path.join(OUT_DIR, "F2_F3_ainsworth_crosstalk.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, cid in zip(axes, ["F2", "F3"]):
        t = results[cid]["windowed_table"]
        ws = [r["window_size_px"] for r in t]
        ax.plot(ws, [r["dop_mean_before"] for r in t], marker="o", label="before calibration")
        ax.plot(ws, [r["dop_mean_after_ainsworth"] for r in t], marker="s", label="after Ainsworth crosstalk cal.")
        ax.axhspan(PAPER_RANGE[0], PAPER_RANGE[1], color="green", alpha=0.15, label="paper range")
        ax.set_title(f"{cid} interior DOP vs window size")
        ax.set_xlabel("covariance window size (px)")
        ax.set_ylabel("linear-pol DOP (interior mean)")
        ax.legend()
        ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "F2_F3_ainsworth_plot.png"), dpi=150)
    plt.close(fig)

    converged = [cid for cid, r in results.items() if r["aggregate_whole_interior_dop"]["meets_paper_range"]]
    summary = {
        "purpose": "Ainsworth et al. 2006 a posteriori crosstalk/channel-imbalance calibration, tested against F2/F3 paper ground truth (0.10-0.13)",
        "algorithm_source": "Ainsworth, Ferro-Famil, Lee, IEEE TGRS 44(4):994-1003, 2006 (read in full via IEEE this session)",
        "known_defect_reference": "Xing, Dai, Liu, Wang, IEEE TGRS 50(6):2417-2419, 2012 (comment paper, read in full via IEEE this session)",
        "craters_meeting_paper_range": converged,
        "verdict": (
            f"{len(converged)} of {len(results)} craters landed within the paper's 0.10-0.13 range after Ainsworth crosstalk calibration."
            if converged else
            "NEITHER crater's DOP moved into the paper's 0.10-0.13 range after implementing and applying the actual Ainsworth 2006 crosstalk/channel-imbalance calibration algorithm (not a self-derived approximation). See per-crater calibration_params for recovered u,v,w,z,alpha and linearization validity; see eta_over_beta for data-quality diagnostics. Reported as the honest outcome, not adjusted."
        ),
        "per_crater": {cid: r["aggregate_whole_interior_dop"] for cid, r in results.items()},
    }
    with open(os.path.join(OUT_DIR, "F2_F3_ainsworth_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n=== VERDICT ===")
    print(summary["verdict"])
    print(f"\nTotal time: {time.time()-t0:.1f}s. Outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
