import numpy as np
import csv
import pandas as pd
import os
import argparse
from astropy.io import fits

def cross_match(catalog_dir, file_dir, threshold_distance, download_filename, download_dir):

    '''
    :param catalog_dir: Directory of catalog compared with
    :param file_dir: Directory of files we are comparing with
    :param threshold_distance: stars that has Ra and Dec in both catalog within this distance is considered as same star. Unit in degree.
    :param download_filename: Filename of the result csv file
    :param download_dir: Directory of the result csv file
    :return: Download a csv file containing cross-match result
    '''

    os.makedirs(download_dir, exist_ok=True)

    # read in the catalog
    asassn_catalog = pd.read_csv(catalog_dir)
    # "/Users/gailrose/Downloads/Cross_match_asassn/asassn_variables_x.csv" on my computer

    print(f"Found catalog in {catalog_dir}")

    # take out useful information, we will need RA and Dec for comparison, class to assign to TESS objects, and id for denoting the asassn id.
    id_asassn_catalog = []
    ra_asassn_catalog = []
    dec_asassn_catalog = []
    class_asassn_catalog = []

    for i in range(len(asassn_catalog["ID"])):
        id_asassn_catalog.append(asassn_catalog["ID"][i])
        ra_asassn_catalog.append(asassn_catalog["RAJ2000"][i])
        dec_asassn_catalog.append(asassn_catalog["DEJ2000"][i])
        class_asassn_catalog.append(asassn_catalog["ML_classification"][i])


    # read in each fits file for TESS objects
    main_directory = file_dir
    # "/Users/gailrose/Downloads/Cross_match_asassn/TESS-Sector01" on my computer

    print(f"Found fits files in {file_dir}")

    # take out useful information from TESS fits files, we need filename and object for classifying each observation, and  RA and Dec for cross-match
    filename_tess_catalog = []
    ra_tess_catalog = []
    dec_tess_catalog = []
    obj_tess_catalog = []

    for root, folder, files in os.walk(main_directory):

            for file_name in files:
                if file_name.endswith('.fits'):
                    fits_dir = os.path.join(root, file_name)
                    #print(file_name)

                    # read the header
                    hdu = fits.open(fits_dir)
                    header = hdu[0].header

                    #print(header)

                    # take RA, DeC, object name, and file name into a catalog
                    filename_tess_catalog.append(file_name)
                    ra_tess_catalog.append(header["RA_OBJ"])
                    dec_tess_catalog.append(header["DEC_OBJ"])
                    obj_tess_catalog.append(header["OBJECT"])

    # list that hold useful information after cross-match
    # we need TESS file name and object name for clarification
    # RA and Dec from both TESS and asassn
    # class is what we need to assign to TESS objects
    info_row = ["TESS file name", "TESS Object", "TESS RA", "TESS Dec", "ASASSN ID", "ASASSN RA", "ASASSN Dec", "ASASSN Class", "RA Separation", "Dec Separation"]
    file_list = [info_row]

    # count how many been successfully matched
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
    # "ASASSN_Cross_Match_Result_Sector01.csv" and "/Users/gailrose/Downloads/Cross_match_asassn" on my computer

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