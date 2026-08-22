"""
PRISM -- memory-safe reader for the raw Chandrayaan-2 DFSAR L0A-RAW product.

Product (fixed for this reader, verified against its own PDS4 label):
  data/ch2_sar_nrxl_20251025t211236510_d_fp_d18/data/raw/20251025/
      ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat   (2,921,247,377 bytes)
      ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.xml   (PDS4 label)

Binary structure, taken directly from the XML label's Array_2D_Image blocks
(NOT assumed):
  - Imaging Frames block: offset=48158 bytes, 1,256,410 lines x 2325 bytes/line,
    Element_Array data_type=SignedByte.
  - Pre-calibration frames: offset=0, 22 lines x 2189 bytes (noise+replica).
  - Post-calibration frames: offset=2,921,201,408, 21 lines x 2189 bytes.
  This reader only exposes the Imaging Frames block (science data).

Per-line layout within the Imaging Frames block (reverse-engineered and
verified in notebooks/objective1_y4r_polarimetry.ipynb.ipynb STEP 8-14, and
independently re-confirmed by this project's dfsar_channel_mapping_verification.json):
  bytes [0:141)      fixed prefix + variable per-pulse header (not decoded here)
  bytes [141:2189)   2048-byte I/Q payload = 1024 complex samples/line
                      (matches XML isda:samples_per_echo_line=1024, 2 bytes/sample)
  bytes [2189:2325)  136-byte constant 0x80 padding tail (not decoded here)

Sample decoding: each payload byte is decoded as OFFSET-BINARY, i.e.
  value = raw_unsigned_byte - 128.0
NOT as a literal PDS4 "SignedByte" (two's-complement) cast. This is an
empirical finding, not the label's literal type: casting the same bytes as
two's-complement int8 produces a discontinuous (wrapped) distribution, while
the offset-binary decode reproduces the XML's per-polarization
standard_deviation_real/imag and bias_real/imag statistics closely for
HV/VH/VV and moderately for HH (see docs/RAW_DFSAR_VALIDATION.md). The
product's own file comment confirms the data is "BAQ uncompressed" raw ADC
I/Q, consistent with offset-binary storage.

Polarization interleave: consecutive raw imaging lines cycle through 4
polarization channels in a fixed 4-way round-robin (line i -> group i % 4).
This matches isda:num_polarizations=4 and isda:pulses_received_per_dwell
=314103 (~= 1,256,410 / 4). Group-to-polarization identity was established
in dfsar_channel_mapping_verification.json by an exhaustive 24-permutation
search against the XML's per-channel std_real/std_imag/bias_real/bias_imag,
run at two sample sizes (N=100, N=4000 lines), with the winning mapping
stable and ranked #1/24 at both sizes:
    G0 -> HV, G1 -> HH, G2 -> VV, G3 -> VH
This mapping is NOT re-derived here; it is imported as a verified constant.
HH's fit is the weakest of the four (see docs/RAW_DFSAR_VALIDATION.md) --
callers should treat HH-dependent results with correspondingly lower
confidence.

No calibration (gain_imbalance, phase_orthogonality correction, nes0 noise
floor) is applied by this reader -- it returns bias-corrected (XML
bias_real/bias_imag subtracted) but otherwise raw complex I/Q samples.
Radiometric/phase calibration is a separate, not-yet-validated step (see
docs/RAW_DFSAR_VALIDATION.md and docs/DOP_VALIDATION.md).

This module never loads the full 2.92 GB file into memory: all reads are
seek + bounded fixed-size reads sized to the requested window.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import numpy as np

DAT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "ch2_sar_nrxl_20251025t211236510_d_fp_d18", "data", "raw",
    "20251025", "ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat",
)

# --- verified binary structure constants (from XML label + byte-level reverse engineering) ---
IMAGING_OFFSET = 48158          # isda Array_2D_Image (Imaging Frames) offset, bytes
LINE_BYTES = 2325               # bytes/line, Imaging Frames axis "Sample" elements
TOTAL_IMAGING_LINES = 1_256_410  # Imaging Frames axis "Line" elements
PAYLOAD_START = 141             # start of 2048-byte I/Q payload within a line
PAYLOAD_END = 2189              # exclusive; PAYLOAD_END - PAYLOAD_START = 2048 = 1024*2
SAMPLES_PER_LINE = 1024         # isda:samples_per_echo_line
N_POL_GROUPS = 4                # isda:num_polarizations

# verified group -> polarization mapping (dfsar_channel_mapping_verification.json,
# best fit at N=100 AND N=4000, rank 1/24 both times)
GROUP_TO_POL = {0: "HV", 1: "HH", 2: "VV", 3: "VH"}
POL_TO_GROUP = {v: k for k, v in GROUP_TO_POL.items()}

# per-polarization bias, from the raw .dat XML label (isda:polarization_info)
XML_BIAS = {
    "HH": (0.086681, 2.846410),
    "HV": (0.206393, 2.980114),
    "VH": (-1.551034, 1.179173),
    "VV": (3.465097, 5.086929),
}
XML_STD = {
    "HH": (12.502030, 12.504541),
    "HV": (4.048946, 4.232149),
    "VH": (5.209197, 5.187600),
    "VV": (11.240361, 10.801348),
}

LINES_PER_POL_CHANNEL = TOTAL_IMAGING_LINES // N_POL_GROUPS  # ~314,102


@dataclass
class DfsarRawReader:
    """Memory-safe windowed reader for the DFSAR L0A-RAW imaging-frame payload.

    `line` indexes are in PER-POLARIZATION-CHANNEL line space
    (0 .. LINES_PER_POL_CHANNEL-1), i.e. line k of channel HH is the k-th
    raw-file line assigned to group G1, not raw byte-file line k.
    `sample` indexes are range-sample indices within [0, SAMPLES_PER_LINE).
    """

    dat_path: str = DAT_PATH
    apply_bias_correction: bool = True

    def __post_init__(self):
        if not os.path.isfile(self.dat_path):
            raise FileNotFoundError(f"Raw DAT not found at {self.dat_path}")
        self._file_size = os.path.getsize(self.dat_path)

    def read_window(self, line_start: int, line_count: int,
                     sample_start: int, sample_count: int) -> dict:
        """Read a small window and return decoded complex arrays per channel.

        Returns a dict:
          {"HH": complex64[line_count, sample_count], "HV": ..., "VH": ..., "VV": ...,
           "line_start": line_start, "line_count": line_count,
           "sample_start": sample_start, "sample_count": sample_count}

        Implementation note: because polarization channels are interleaved
        4-way across consecutive RAW file lines, producing `line_count`
        output lines per channel requires reading `4 * line_count`
        consecutive raw lines starting at raw line `4 * line_start`. This is
        still a single bounded contiguous read (no mmap of the whole file,
        no full-file load).
        """
        if line_start < 0 or line_count <= 0:
            raise ValueError("line_start must be >=0 and line_count > 0")
        if sample_start < 0 or sample_count <= 0 or sample_start + sample_count > SAMPLES_PER_LINE:
            raise ValueError(f"sample range [{sample_start}, {sample_start + sample_count}) "
                              f"out of bounds [0, {SAMPLES_PER_LINE})")
        if line_start + line_count > LINES_PER_POL_CHANNEL:
            raise ValueError(f"line range exceeds available per-channel lines "
                              f"({LINES_PER_POL_CHANNEL})")

        raw_line_start = 4 * line_start
        n_raw_lines = 4 * line_count
        byte_start = IMAGING_OFFSET + raw_line_start * LINE_BYTES
        n_bytes = n_raw_lines * LINE_BYTES

        if byte_start + n_bytes > self._file_size:
            raise ValueError("requested window extends past end of file")

        with open(self.dat_path, "rb") as f:
            f.seek(byte_start)
            raw = f.read(n_bytes)
        if len(raw) != n_bytes:
            raise IOError(f"short read: expected {n_bytes} bytes, got {len(raw)}")

        lines = np.frombuffer(raw, dtype=np.uint8).reshape(n_raw_lines, LINE_BYTES)
        payload = lines[:, PAYLOAD_START:PAYLOAD_END]  # (n_raw_lines, 2048) uint8

        # offset-binary decode (see module docstring)
        I = payload[:, 0::2].astype(np.float32) - 128.0
        Q = payload[:, 1::2].astype(np.float32) - 128.0
        complex_all = (I + 1j * Q).astype(np.complex64)  # (n_raw_lines, 1024)

        out = {
            "line_start": line_start, "line_count": line_count,
            "sample_start": sample_start, "sample_count": sample_count,
        }
        for group_idx, pol in GROUP_TO_POL.items():
            chan = complex_all[group_idx::4, sample_start:sample_start + sample_count]
            if self.apply_bias_correction:
                br, bi = XML_BIAS[pol]
                chan = chan - complex(br, bi)
            out[pol] = chan
        return out

    def metadata(self) -> dict:
        return {
            "dat_path": self.dat_path,
            "file_size_bytes": self._file_size,
            "imaging_offset": IMAGING_OFFSET,
            "line_bytes": LINE_BYTES,
            "total_imaging_lines": TOTAL_IMAGING_LINES,
            "payload_start": PAYLOAD_START,
            "payload_end": PAYLOAD_END,
            "samples_per_line": SAMPLES_PER_LINE,
            "n_pol_groups": N_POL_GROUPS,
            "lines_per_pol_channel": LINES_PER_POL_CHANNEL,
            "group_to_pol": GROUP_TO_POL,
            "apply_bias_correction": self.apply_bias_correction,
        }
