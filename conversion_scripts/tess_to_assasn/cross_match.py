import numpy as np
import csv
import pandas as pd
import os
import argparse
from astropy.io import fits

def cross_match(catalog_dir, file_dir, threshold_distance, download_filename, download_dir):
    os.makedirs(download_dir, exist_ok=True)

    asassn_catalog = pd.read_csv(catalog_dir)

    print(f"Found catalog in {catalog_dir}")

    id_asassn_catalog = []
    ra_asassn_catalog = []
    dec_asassn_catalog = []
    class_asassn_catalog = []

    for i in range(len(asassn_catalog["ID"])):
        id_asassn_catalog.append(asassn_catalog["ID"][i])
        ra_asassn_catalog.append(asassn_catalog["RAJ2000"][i])
        dec_asassn_catalog.append(asassn_catalog["DEJ2000"][i])
        class_asassn_catalog.append(asassn_catalog["ML_classification"][i])


    main_directory = file_dir

    print(f"Found fits files in {file_dir}")

    filename_tess_catalog = []
    ra_tess_catalog = []
    dec_tess_catalog = []
    obj_tess_catalog = []

    for root, folder, files in os.walk(main_directory):

            for file_name in files:
                if file_name.endswith('.fits'):
                    fits_dir = os.path.join(root, file_name)

                    hdu = fits.open(fits_dir)
                    header = hdu[0].header

                    filename_tess_catalog.append(file_name)
                    ra_tess_catalog.append(header["RA_OBJ"])
                    dec_tess_catalog.append(header["DEC_OBJ"])
                    obj_tess_catalog.append(header["OBJECT"])

    info_row = ["TESS file name", "TESS Object", "TESS RA", "TESS Dec", "ASASSN ID", "ASASSN RA", "ASASSN Dec", "ASASSN Class", "RA Separation", "Dec Separation"]
    file_list = [info_row]

    count = 0

    for i in range(len(ra_tess_catalog)):

        obj_row = [filename_tess_catalog[i], obj_tess_catalog[i], ra_tess_catalog[i], dec_tess_catalog[i],
                   "", "", "", "",
                   "", ""]

        for j in range(len(id_asassn_catalog)):

            if (float(ra_asassn_catalog[j]) - float(threshold_distance) <= ra_tess_catalog[i] <= float(ra_asassn_catalog[j]) + float(threshold_distance)) and (
            float((dec_asassn_catalog[j]) - float(threshold_distance) <= dec_tess_catalog[i] <= float(dec_asassn_catalog[j]) + float(threshold_distance))):

                obj_row[4:10] = [id_asassn_catalog[j], ra_asassn_catalog[j], dec_asassn_catalog[j], class_asassn_catalog[j],
                                 np.absolute(ra_asassn_catalog[j] - ra_tess_catalog[i]), np.absolute(dec_asassn_catalog[j] - dec_tess_catalog[i])]

                count += 1

                print(f"Total number of matched stars: {count}")

        file_list.append(obj_row)


    output_fullpath = os.path.join(download_dir, download_filename)

    with open(output_fullpath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(file_list)

    print(f"Cross-match completed. CSV files saved in {output_fullpath}")
    print(f"Successfully matched {count} stars")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog_dir", type=str, required=True)
    parser.add_argument("--file_dir", type=str, required=True)
    parser.add_argument("--threshold_distance", type=float, required=True)
    parser.add_argument("--download_filename", type=str, required=True)
    parser.add_argument("--download_dir", type=str, required=True)
    args = parser.parse_args()

    CATALOG_DIR = args.catalog_dir
    FILE_DIR = args.file_dir
    THRESHOLD_DISTANCE = args.threshold_distance
    DOWNLOAD_FILENAME = args.download_filename
    DOWNLOAD_DIR = args.download_dir

    cross_match(CATALOG_DIR, FILE_DIR, THRESHOLD_DISTANCE, DOWNLOAD_FILENAME, DOWNLOAD_DIR)