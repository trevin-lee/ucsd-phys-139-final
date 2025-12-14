import os
import argparse
import pandas as pd
import numpy as np
from astropy.io import fits
import csv

from sklearn.neighbors import KDTree 


def _radec_to_unitvec(ra_deg, dec_deg):
    ra = np.deg2rad(ra_deg)
    dec = np.deg2rad(dec_deg)
    cosd = np.cos(dec)

    x = cosd * np.cos(ra)
    y = cosd * np.sin(ra)
    z = np.sin(dec)
    return np.column_stack([x, y, z])


def cross_match_asassn(catalog_path, fits_dir, threshold_degree, output_filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    df = pd.read_csv(catalog_path)

    try:
        id_asassn = df["ID"].values
        ra_asassn = df["RAJ2000"].values
        dec_asassn = df["DEJ2000"].values
        class_asassn = df["ML_classification"].values
    except KeyError as e:
        return

    print(f"Loaded {len(df)} ASASSN")

    asassn_vecs = _radec_to_unitvec(ra_asassn, dec_asassn)
    tree = KDTree(asassn_vecs, metric="euclidean")

    theta_rad = np.deg2rad(threshold_degree)
    radius = 2.0 * np.sin(theta_rad / 2.0)

    tess_files = []
    tess_ra = []
    tess_dec = []

    for root, _, files in os.walk(fits_dir):
        for fname in files:
            if fname.endswith(".fits"):
                path = os.path.join(root, fname)

                try:
                    with fits.open(path) as hdul:
                        hdr = hdul[0].header
                        if "RA_OBJ" in hdr and "DEC_OBJ" in hdr:
                            tess_files.append(fname)
                            tess_ra.append(hdr["RA_OBJ"])
                            tess_dec.append(hdr["DEC_OBJ"])
                except Exception as e:
                    continue

    n_tess = len(tess_files)
    print(f"Found {n_tess} TESS light curves with coordinates")

    if n_tess == 0:
        print("No TESS files with RA_OBJ/DEC_OBJ found; exiting")
        return

    tess_ra = np.array(tess_ra)
    tess_dec = np.array(tess_dec)

    tess_vecs = _radec_to_unitvec(tess_ra, tess_dec)

    idxs_list = tree.query_radius(tess_vecs, r=radius)

    results = []

    for i in range(n_tess):
        fname = tess_files[i]
        idxs = idxs_list[i]

        if len(idxs) > 0:
            j = idxs[-1]
            star_id = id_asassn[j]
            label = class_asassn[j]
        else:
            star_id = fname.replace(".fits", "")
            label = "Unknown"

        results.append([star_id, label])

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["star_id", "label"])
        writer.writerows(results)

    print(f"Total rows: {len(results)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--catalog_path", required=True)
    parser.add_argument("--fits_dir", required=True)
    parser.add_argument("--threshold_degree", type=float, default=0.01)
    parser.add_argument("--output_filename", default="labels.csv")
    parser.add_argument("--output_dir", default=".")

    args = parser.parse_args()

    cross_match_asassn(
        args.catalog_path,
        args.fits_dir,
        args.threshold_degree,
        args.output_filename,
        args.output_dir
    )
