import argparse
import os
from .tess_downloader import download_tess_light_curves
from .gaia_downloader import download_gaia_data
from .asassn_downloader import download_asassn_catalog

def main():
    parser = argparse.ArgumentParser(description="Master dataset downloader and processor.")

    parser.add_argument("--tess_sector", type=int, default=10, help="TESS Sector to download (default: 10)")
    parser.add_argument("--tess_max_files", type=int, default=20000, help="Max TESS files (default: 20000)")
    parser.add_argument("--tess_dir", type=str, default="data/tess_sector10", help="TESS download directory")

    parser.add_argument("--gaia_dir", type=str, default="data/gaia", help="Gaia download directory")
    parser.add_argument("--gaia_files", type=int, default=2, help="Number of Gaia files to download")

    parser.add_argument("--asassn_dir", type=str, default="data/asassn", help="ASASSN download directory")
    parser.add_argument("--asassn_filename", type=str, default="asassn_variables_x.csv", help="ASASSN filename")

    parser.add_argument("--skip_tess", action="store_true", help="Skip TESS download")
    parser.add_argument("--skip_gaia", action="store_true", help="Skip Gaia download")
    parser.add_argument("--skip_asassn", action="store_true", help="Skip ASASSN download")
    parser.add_argument("--run_all", action="store_true", help="Run all steps (TESS, Gaia, ASASSN download)")

    args = parser.parse_args()
    
    run_tess = not args.skip_tess
    run_gaia = args.run_all and not args.skip_gaia
    run_asassn = args.run_all and not args.skip_asassn

    if run_tess:
        print("\n=== TESS Data Download ===")
        download_tess_light_curves(args.tess_sector, args.tess_max_files, args.tess_dir)
        
    if run_gaia:
        print("\n=== Gaia Data Download ===")
        download_gaia_data(args.gaia_dir, args.gaia_files)
        
    if run_asassn:
        print("\n=== ASASSN Data Download ===")
        download_asassn_catalog(args.asassn_dir, args.asassn_filename)

if __name__ == "__main__":
    main()
