###################################################################################################
#
#                                       TRANSFER EXIF DATA
#
#
# Transfers GPS data to image metadata.
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-06-04
#
# Algorithm:
#   1. Import gps data from GPS file
#   2. Move data to the images
#
###################################################################################################
import os
import json
import argparse

from GPSPhoto import gpsphoto
from pathlib import Path

###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
JPG = ".JPG"
PNG = ".PNG"

###################################################################################################
#
#                                            CLASSES
#
###################################################################################################


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def add_GPS_metadata(data_folder):

    gps_file_path = Path(data_folder, "GPS_data.csv")

    assert os.path.exists(data_folder), "Data Folder does not exist."
    assert os.path.exists(gps_file_path), "GPS data file not found."

    # Get names of the exif data files
    dir_files = os.listdir(data_folder)

    image_files = []
    for image in dir_files:
        if JPG in image:
            image_files = image_files + [image]

    image_format = JPG

    if image_files is []:
        image_format = PNG
        for image in dir_files:
            if PNG in image:
                image_files = image_files + [image]

    if image_files is []:
        print("No image files ending with .jpg or .png in folder: " + str(data_folder))

    with open(gps_file_path, 'r') as gps_file:
        # For each line in the file, read the image name, match it , and add data
        for line in gps_file.readlines():

            image_name, lat, lon, alt = line.split(",")

            # Add image end if there
            if image_name[-5:-1] is not image_format:
                image_name = image_name + image_format

            alt = alt[0:-1] # Strip \n char

            # Ensure image is in the image files
            if not image_name in image_files:
                print("Image " + image_name + " not found in image files. Cannot move exif data")
                continue

            # Append gps data to file
            photo = gpsphoto.GPSPhoto(str(Path(data_folder, image_name)))
            info = gpsphoto.GPSInfo((float(lat), float(lon)), int(alt))

            photo.modGPSData(info, str(Path(data_folder, image_name)))


# Insertion point
if __name__ == '__main__':
    # Read in arguments
    parser = argparse.ArgumentParser(description='Find slopes from a ply file')
    parser.add_argument('--data_folder', metavar='folder', type=str, default=Path('Data', 'Usmans_data', 'inputs'), help='Image & GPS file folder path')
    args = parser.parse_args()

    add_GPS_metadata(args.data_folder)
