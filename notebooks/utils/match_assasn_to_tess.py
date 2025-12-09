import os
import argparse
import pandas as pd
import numpy as np
from astropy.io import fits
import csv

from sklearn.neighbors import KDTree  # <- NEW


def _radec_to_unitvec(ra_deg, dec_deg):
    """
    Convert RA, Dec (in degrees) to 3D unit vectors on the sphere.
    """
    ra = np.deg2rad(ra_deg)
    dec = np.deg2rad(dec_deg)
    cosd = np.cos(dec)

    x = cosd * np.cos(ra)
    y = cosd * np.sin(ra)
    z = np.sin(dec)
    return np.column_stack([x, y, z])


def cross_match_asassn(catalog_path, fits_dir, threshold_degree, output_filename, output_dir):
    """
    Cross-match ASASSN variable catalog with TESS FITS files.
    Output: ONLY (star_id, label) per TESS FITS file.

    Now uses a KD-tree in 3D unit-vector space for fast radius queries.
    """

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    # --------------------------
    # Load ASASSN catalog
    # --------------------------
    print(f"📖 Reading ASASSN catalog: {catalog_path}")
    df = pd.read_csv(catalog_path)

    try:
        id_asassn = df["ID"].values
        ra_asassn = df["RAJ2000"].values
        dec_asassn = df["DEJ2000"].values
        class_asassn = df["ML_classification"].values
    except KeyError as e:
        print(f"❌ Missing required column: {e}")
        print("Columns present:", df.columns)
        return

    print(f"Loaded {len(df)} ASASSN entries.")

    # --------------------------
    # Build KD-tree on ASASSN positions (3D unit vectors)
    # --------------------------
    print("🧱 Building KD-tree on ASASSN coordinates...")
    asassn_vecs = _radec_to_unitvec(ra_asassn, dec_asassn)
    tree = KDTree(asassn_vecs, metric="euclidean")

    # Convert threshold (deg) to a chord distance in 3D:
    # angular separation = theta (rad)
    # chord distance d = 2 * sin(theta/2)
    theta_rad = np.deg2rad(threshold_degree)
    radius = 2.0 * np.sin(theta_rad / 2.0)
    print(f"Using KD-tree radius = {radius:.6e} (chord in 3D) for {threshold_degree} deg")

    # --------------------------
    # Scan TESS FITS files
    # --------------------------
    print(f"🔍 Searching TESS FITS in: {fits_dir}")

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
                    print(f"⚠️ Failed to read {fname}: {e}")

    n_tess = len(tess_files)
    print(f"Found {n_tess} TESS light curves with coordinates.")

    if n_tess == 0:
        print("No TESS files with RA_OBJ/DEC_OBJ found; exiting.")
        return

    tess_ra = np.array(tess_ra)
    tess_dec = np.array(tess_dec)

    # Convert TESS coords to unit vectors
    tess_vecs = _radec_to_unitvec(tess_ra, tess_dec)

    # --------------------------
    # KD-tree radius queries
    # --------------------------
    print(f"⚙️ Matching with KD-tree (threshold {threshold_degree} deg)…")

    # Query all at once: returns array of index arrays
    idxs_list = tree.query_radius(tess_vecs, r=radius)

    results = []

    for i in range(n_tess):
        fname = tess_files[i]
        idxs = idxs_list[i]

        if len(idxs) > 0:
            # Following your original logic: take the "last" match
            j = idxs[-1]
            star_id = id_asassn[j]
            label = class_asassn[j]
        else:
            # No match: assign "Unknown" label, keep TESS file name as ID
            star_id = fname.replace(".fits", "")
            label = "Unknown"

        results.append([star_id, label])

    # --------------------------
    # Write output: 2-column CSV
    # --------------------------
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["star_id", "label"])
        writer.writerows(results)

    print(f"\n✅ DONE! Saved 2-column CSV to:\n   {output_path}")
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
