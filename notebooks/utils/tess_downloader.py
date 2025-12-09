from astroquery.mast import Observations
import os
import argparse


from astroquery.mast import Observations
import os
import numpy as np

def download_tess_light_curves(sector, max_files=None, download_dir="tess_data", lc_only=True):

    os.makedirs(download_dir, exist_ok=True)

    print(f"🔍 Searching for 2-minute cadence TESS light curves from Sector {sector}...")
    obs = Observations.query_criteria(
        project="TESS",
        dataproduct_type="timeseries",
        sequence_number=sector,
        t_exptime=(100, 130)  # ~120 s cadence
    )
    print(f"Found {len(obs)} observations.")

    if len(obs) == 0:
        print("⚠️ No observations found for that sector.")
        return

    products = Observations.get_product_list(obs)

    if lc_only:
        products = Observations.filter_products(
            products,
            productSubGroupDescription="LC",  # *_lc.fits
            productType="SCIENCE"
        )
        print(f"Filtered to {len(products)} light-curve products (LC only).")

    if max_files:
        products = products[:max_files]

    total_gb = float(np.nansum(products['size'])) / 1024**3
    print(f"Estimated total size: ~{total_gb:.2f} GB for {len(products)} products.")

    # Confirm download
    print(f"⬇️  Starting download to: {download_dir}")
    manifest = Observations.download_products(
        products,
        download_dir=download_dir,
        mrp_only=True if lc_only else False,  # keep only necessary files
        curl_flag=False,
        cache=True
    )

    print(f"\n✅ Download complete! Files saved in '{download_dir}'")
    print(f"Downloaded {len(manifest)} products.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sector", type=int, required=True)
    parser.add_argument("--max_files", type=int, required=True)
    parser.add_argument("--download_dir", type=str, required=True)
    args = parser.parse_args()

    SECTOR = args.sector
    MAX_FILES = args.max_files
    DOWNLOAD_DIR = args.download_dir
   
    download_tess_light_curves(SECTOR, MAX_FILES, DOWNLOAD_DIR)
