import os
import argparse
import pandas as pd
import numpy as np
import csv
from astropy.io import fits

def cross_match_asassn(catalog_path, fits_dir, threshold_degree, output_filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    print(f"Reading ASASSN catalog from: {catalog_path}")
    if not os.path.exists(catalog_path):
        print(f"Error: Catalog file not found at {catalog_path}")
        return

    try:
        asassn_catalog = pd.read_csv(catalog_path)
    except Exception as e:
        print(f"Error reading catalog: {e}")
        return

    try:
        id_asassn = asassn_catalog["ID"].values
        ra_asassn = asassn_catalog["RAJ2000"].values
        dec_asassn = asassn_catalog["DEJ2000"].values
        class_asassn = asassn_catalog["ML_classification"].values
    except KeyError as e:
        print(f"Error: Missing column in ASASSN catalog: {e}")
        return

    print(f"Loaded {len(asassn_catalog)} ASASSN sources.")

    print(f"Searching for FITS files in: {fits_dir}")
    if not os.path.exists(fits_dir):
        print(f"Error: FITS directory not found at {fits_dir}")
        return

    tess_files = []
    tess_ra = []
    tess_dec = []
    tess_obj = []

    for root, _, files in os.walk(fits_dir):
        for file_name in files:
            if file_name.endswith('.fits'):
                file_path = os.path.join(root, file_name)
                try:
                    with fits.open(file_path) as hdu:
                        header = hdu[0].header
                        if "RA_OBJ" in header and "DEC_OBJ" in header:
                            tess_files.append(file_name)
                            tess_ra.append(header["RA_OBJ"])
                            tess_dec.append(header["DEC_OBJ"])
                            tess_obj.append(header.get("OBJECT", "Unknown"))
                except Exception as e:
                    print(f"Warning: Failed to read {file_name}: {e}")

    print(f"Found {len(tess_files)} TESS FITS files.")

    if len(tess_files) == 0:
        print("No TESS files found. Exiting.")
        return

    headers = ["TESS file name", "TESS Object", "TESS RA", "TESS Dec", 
               "ASASSN ID", "ASASSN RA", "ASASSN Dec", "ASASSN Class", 
               "RA Separation", "Dec Separation"]
    results = []

    count = 0
    print(f"Starting cross-match with threshold {threshold_degree} deg...")
    
    tess_ra_arr = np.array(tess_ra)
    tess_dec_arr = np.array(tess_dec)

    for i in range(len(tess_files)):
        t_ra = tess_ra_arr[i]
        t_dec = tess_dec_arr[i]
        
        ra_diff = np.abs(ra_asassn - t_ra)
        dec_diff = np.abs(dec_asassn - t_dec)
        
        mask = (ra_diff <= threshold_degree) & (dec_diff <= threshold_degree)
        
        matches_indices = np.where(mask)[0]
        
        matched_data = ["", "", "", "", "", ""]
        
        if len(matches_indices) > 0:
            idx = matches_indices[-1] 
            
            matched_data = [
                id_asassn[idx],
                ra_asassn[idx],
                dec_asassn[idx],
                class_asassn[idx],
                ra_diff[idx],
                dec_diff[idx]
            ]
            count += 1
            if count % 100 == 0:
                print(f"Matched {count} stars so far...")

        row = [
            tess_files[i],
            tess_obj[i],
            t_ra,
            t_dec
        ] + matched_data
        
        results.append(row)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)

    print(f"\nCross-match complete! Saved to: {output_path}")
    print(f"Total matches found: {count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match objects from ASASSN to TESS.")

    default_catalog = "data/asassn/asassn_variables_x.csv"
    default_output_dir = "data/asassn"

    parser.add_argument("--catalog_path", type=str, default=default_catalog, help="Path to ASASSN catalog CSV")
    parser.add_argument("--fits_dir", type=str, required=True, help="Directory containing TESS FITS files")
    parser.add_argument("--threshold_degree", type=float, default=0.01, help="Match threshold in degrees")
    parser.add_argument("--output_filename", type=str, default="asassn_crossmatch.csv", help="Output filename")
    parser.add_argument("--output_dir", type=str, default=default_output_dir, help="Output directory")

    args = parser.parse_args()

    cross_match_asassn(
        args.catalog_path,
        args.fits_dir,
        args.threshold_degree,
        args.output_filename,
        args.output_dir
    )

