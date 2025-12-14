import os
import argparse
import pandas as pd
import glob
from astropy.coordinates import SkyCoord, search_around_sky
from astropy import units as u
from astropy.io import fits

def cross_match_gaia(gaia_folder, tess_fits_dir, threshold_degree, output_filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    print(f"Loading Gaia data from: {gaia_folder}")
    gaia_files = glob.glob(os.path.join(gaia_folder, "*.csv*"))

    if not gaia_files:
        print("No CSV files found in Gaia directory!")
        return

    gaia_dfs = []
    for file in gaia_files:
        try:
            print(f"   Reading {os.path.basename(file)}...")
            df = pd.read_csv(file, comment='#')
            gaia_dfs.append(df)
        except Exception as e:
            print(f"   Error reading {file}: {e}")

    if not gaia_dfs:
        print("Could not load any Gaia data.")
        return

    gaia_catalog = pd.concat(gaia_dfs, ignore_index=True)
    print(f"   Loaded {len(gaia_catalog)} Gaia stars.")

    gaia_ra_col = 'ra'
    gaia_dec_col = 'dec'
    gaia_id_col = 'source_id'
    
    if gaia_ra_col not in gaia_catalog.columns:
        if 'RA' in gaia_catalog.columns:
             gaia_ra_col = 'RA'
             gaia_dec_col = 'DEC'
             gaia_id_col = 'SOURCE_ID'
        else:
             print(f"Error: RA column not found in Gaia data. Columns: {gaia_catalog.columns}")
             return


    print(f"Loading TESS data from FITS headers in: {tess_fits_dir}")
    tess_files = []
    tess_ra = []
    tess_dec = []
    tess_obj = []

    for root, _, files in os.walk(tess_fits_dir):
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
                    pass

    if not tess_files:
        print("No valid TESS FITS files found.")
        return

    tess_catalog = pd.DataFrame({
        'filename': tess_files,
        'object': tess_obj,
        'ra': tess_ra,
        'dec': tess_dec
    })
    
    print(f"   Loaded {len(tess_catalog)} TESS targets.")

    print(f"Matching with threshold: {threshold_degree} deg...")

    c_gaia = SkyCoord(ra=gaia_catalog[gaia_ra_col].values * u.degree,
                      dec=gaia_catalog[gaia_dec_col].values * u.degree)

    c_tess = SkyCoord(ra=tess_catalog['ra'].values * u.degree,
                      dec=tess_catalog['dec'].values * u.degree)

    idx_tess, idx_gaia, d2d, d3d = search_around_sky(c_tess, c_gaia, threshold_degree * u.degree)

    print(f"   Found {len(idx_tess)} matches.")

    matches_tess = tess_catalog.iloc[idx_tess].reset_index(drop=True)
    matches_gaia = gaia_catalog.iloc[idx_gaia].reset_index(drop=True)

    result_df = pd.DataFrame({
        'TESS_Filename': matches_tess['filename'],
        'TESS_Object': matches_tess['object'],
        'TESS_RA': matches_tess['ra'],
        'TESS_Dec': matches_tess['dec'],
        'Gaia_ID': matches_gaia[gaia_id_col],
        'Gaia_RA': matches_gaia[gaia_ra_col],
        'Gaia_Dec': matches_gaia[gaia_dec_col],
        'Separation_Deg': d2d.value
    })

    if 'best_class_name' in matches_gaia.columns:
        result_df['Gaia_Class'] = matches_gaia['best_class_name']
    elif 'ML_classification' in matches_gaia.columns:
        result_df['Gaia_Class'] = matches_gaia['ML_classification']
    elif 'classprob_dsc_combmod_quasar' in matches_gaia.columns:
         pass

    result_df.to_csv(output_path, index=False)
    print(f"\nMatch results saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match objects from Gaia to TESS.")
    
    default_gaia_dir = "data/gaia"
    default_output_dir = "data/gaia_crossmatch"
    
    parser.add_argument("--gaia_dir", type=str, default=default_gaia_dir, help="Directory containing Gaia CSV files")
    parser.add_argument("--fits_dir", type=str, required=True, help="Directory containing TESS FITS files")
    parser.add_argument("--threshold_degree", type=float, default=0.01, help="Match threshold in degrees")
    parser.add_argument("--output_filename", type=str, default="gaia_crossmatch.csv", help="Output filename")
    parser.add_argument("--output_dir", type=str, default=default_output_dir, help="Output directory")

    args = parser.parse_args()

    cross_match_gaia(
        args.gaia_dir,
        args.fits_dir,
        args.threshold_degree,
        args.output_filename,
        args.output_dir
    )

