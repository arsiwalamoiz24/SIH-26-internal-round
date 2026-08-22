import os
import rasterio
from rasterio.windows import Window
import numpy as np
from scipy.ndimage import uniform_filter
import glob

def find_file(base_dir, pattern):
    files = glob.glob(os.path.join(base_dir, "**", f"*{pattern}*"), recursive=True)
    if not files:
        raise FileNotFoundError(f"Could not find file matching pattern {pattern} in {base_dir}")
    return files[0]

def process_block(win, src_hh, src_hv, src_vh, src_vv, win_size=5):
    # Read complex arrays
    # rasterio reads as shape (bands, rows, cols)
    hh_data = src_hh.read(window=win)
    hv_data = src_hv.read(window=win)
    vh_data = src_vh.read(window=win)
    vv_data = src_vv.read(window=win)

    # Convert 2 bands (real, imag) to complex numpy arrays
    hh = hh_data[0] + 1j * hh_data[1]
    hv = hv_data[0] + 1j * hv_data[1]
    vh = vh_data[0] + 1j * vh_data[1]
    vv = vv_data[0] + 1j * vv_data[1]

    # Assume Left Circular (LCP) transmit
    # Receive Horizontal and Vertical
    # Note: Using standard convention for LCP synthesis
    E_H = (hh + 1j * hv) / np.sqrt(2)
    E_V = (vh + 1j * vv) / np.sqrt(2)

    # Calculate instantaneous Stokes parameters
    s1 = np.abs(E_H)**2 + np.abs(E_V)**2
    s2 = np.abs(E_H)**2 - np.abs(E_V)**2
    s3 = 2 * np.real(E_H * np.conj(E_V))
    s4 = 2 * np.imag(E_H * np.conj(E_V))

    # Apply spatial multi-looking (averaging)
    # Using a uniform filter (boxcar)
    s1_avg = uniform_filter(s1, size=win_size, mode='reflect')
    s2_avg = uniform_filter(s2, size=win_size, mode='reflect')
    s3_avg = uniform_filter(s3, size=win_size, mode='reflect')
    s4_avg = uniform_filter(s4, size=win_size, mode='reflect')

    # Add small epsilon to prevent division by zero
    eps = 1e-10

    # Calculate DOP
    dop = np.sqrt(s2_avg**2 + s3_avg**2 + s4_avg**2) / (s1_avg + eps)
    
    # Calculate CPR
    cpr = np.abs((s1_avg - s4_avg) / (s1_avg + s4_avg + eps))

    return dop.astype(np.float32), cpr.astype(np.float32)

def main():
    base_dir = "ch2_sar_ncxl_20191112t041152547_d_fp_gds"
    print("Finding complex _sli_ files...")
    
    hh_path = find_file(base_dir, "_sli_xx_fp_hh_gds.tif")
    hv_path = find_file(base_dir, "_sli_xx_fp_hv_gds.tif")
    vh_path = find_file(base_dir, "_sli_xx_fp_vh_gds.tif")
    vv_path = find_file(base_dir, "_sli_xx_fp_vv_gds.tif")

    print(f"Opening:\n  {hh_path}\n  {hv_path}\n  {vh_path}\n  {vv_path}")

    # Output files
    out_dop_path = "DOP.tif"
    out_cpr_path = "CPR.tif"

    with rasterio.open(hh_path) as src_hh, \
         rasterio.open(hv_path) as src_hv, \
         rasterio.open(vh_path) as src_vh, \
         rasterio.open(vv_path) as src_vv:
        
        # Verify sizes match
        assert src_hh.shape == src_hv.shape == src_vh.shape == src_vv.shape
        height, width = src_hh.shape
        
        print(f"Image dimensions: {width} x {height}")
        
        # Create output profiles
        profile = src_hh.profile
        profile.update(
            dtype=rasterio.float32,
            count=1,
            compress='lzw'
        )

        block_height = 2048
        
        with rasterio.open(out_dop_path, 'w', **profile) as dst_dop, \
             rasterio.open(out_cpr_path, 'w', **profile) as dst_cpr:
            
            for row_start in range(0, height, block_height):
                row_end = min(row_start + block_height, height)
                h = row_end - row_start
                win = Window(0, row_start, width, h)
                
                print(f"Processing block rows {row_start} to {row_end}...", end='\r')
                
                dop_block, cpr_block = process_block(win, src_hh, src_hv, src_vh, src_vv, win_size=5)
                
                # Write to output
                dst_dop.write(dop_block, 1, window=win)
                dst_cpr.write(cpr_block, 1, window=win)

    print("\nProcessing complete! Generated DOP.tif and CPR.tif")

if __name__ == "__main__":
    main()
