###################################################################################################
#
#                                  IMAGE PARSING MODULE
#
#
# Moves images to appropriate folder, formats gps data from images 
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-03-26
# 
# Arguments:
#   image_parsing.py <image_folder_path> <gps_data_file_path>
#
# Module Actions:
#   1. Read Input Directory and GPS file from Arguments
#   2. Move Images to correct directory
#   3. Add config.yaml file
#   4. Read location file
#   5. Match GPS location to images
#   5. Create exif_overrides file in images folder
#
###################################################################################################
import argparse
from pathlib import Path
import os
import shutil
import sys
import json
from datetime import datetime

###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
IMAGE_DIR = "imageData/"
NESTED_IMAGE_DIR = "images/"
GPS_OVERRIDE_FILE = "exif_overrides.json"
CONFIG_YAML = "config.yaml"

MATCHING_GPS_NEIGHBOURS = 4     # Number of images to match selected by GPS distance. Set to 0 to use no limit ** what is best here?
PROCESSES = 4                   # Number of threads to use

GPS_POINT_NUM_I = 0
GPS_LAT_I = 8
GPS_LON_I = 9
GPS_ALT_I = 10
DEFAULT_GPS_DOP = 5.0

IMAGE_FILE_EXT = ".jpg"
IMAGE_DNE = "DNE"

READ_FILE = "r"
WRITE_FILE = "w"


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def validate_args(images_folder, gps_data_file):
    # Validate images folder
    if not os.path.isdir(images_folder):
        print("The image folder path is not a valid directory. Value provided: '" + images_folder + "'")
        exit()
    
    # Validate gps_data file exists
    try:
        file = open(gps_data_file, READ_FILE)
        file.close()
    except IOError as err:
        print("The gps_data file either does not exist or could not be read. Value provided: '" + gps_data_file + "'")
        exit()

    return


def transfer_images(image_folder_path):
    # Remove existsing directory if it exists
    if os.path.isdir(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)

    # Make Directory for images
    os.mkdir(IMAGE_DIR)
    os.mkdir(IMAGE_DIR + NESTED_IMAGE_DIR)

    # Move files from image directory
    for file_name in os.listdir(image_folder_path):
        shutil.copy(image_folder_path + "/" + file_name, IMAGE_DIR + file_name)
        # We can use move instead and that will remove the files from their existsing dir. What behaviour do we want?

    return


def add_config_file():
    config_file = open(IMAGE_DIR + CONFIG_YAML, 'w')

    # Add File Header Comment
    config_file.write('#'*99+'\n')
    config_file.write("#\n")
    config_file.write("#                                         CONFIG.YAML\n")
    config_file.write("#\n")
    config_file.write("#\n")
    config_file.write("# Defines override configuration paramaters for image processing pipeline\n")
    config_file.write("# Authors: Highfly Technologies\n")
    config_file.write("# Creation Date: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
    config_file.write("#\n")
    config_file.write('#'*99+'\n')

    config_file.write("feature_min_frames: " + str(MATCHING_GPS_NEIGHBOURS) + "\n")
    config_file.write("processes: " + str(PROCESSES) + "\n")

    config_file.close()

    return


def read_gps_data(gps_file_path):
    # Access file contents
    gps_data = open(gps_file_path, READ_FILE)
    file_lines = gps_data.readlines()
    gps_data.close()

    expected_gps_point = 0
    gps_data_points = []

    # File Values: gps_point_num X X X X X X X Lon Lat Alt X
    for line in file_lines:
        values = line.split("\t")

        # Check if line has valid data
        if values[GPS_POINT_NUM_I] == str(expected_gps_point): 
            gps_image = GPS_IMAGE(expected_gps_point, expected_gps_point, values[GPS_LAT_I], values[GPS_LON_I], values[GPS_ALT_I], DEFAULT_GPS_DOP)
            gps_data_points.append(gps_image)
            expected_gps_point += 1

    

    return gps_data_points


def match_gps_to_images(gps_data_points):
    # Get image list
    files_anyCase = os.listdir(IMAGE_DIR)
    files = list(map(lambda x: x.lower(), files_anyCase))
    
    # Search image list for each image and update image_name
    for gps_point in gps_data_points:
        gps_point.check_for_image(files)

    return gps_data_points


def create_gps_overrides(gps_image_matches): # gps_image_matches: [GPS_IMAGE]
    exif_overrides = {}

    # Create JSON object
    for gps_image_match in gps_image_matches:
        if gps_image_match.image_name != IMAGE_DNE:
            exif_overrides[gps_image_match.image_name] = gps_image_match.format_gps_data()

    # Write JSON object to file
    with open(IMAGE_DIR + GPS_OVERRIDE_FILE, WRITE_FILE) as outfile:
        json.dump(exif_overrides, outfile)

    return 0

###################################################################################################
#
#                                            CLASSES
#
###################################################################################################
class GPS_IMAGE:
    def __init__ (self, image_name, gps_point_num, gps_lat, gps_long, gps_alt, gps_dop):
        self.image_name = image_name
        self.gps_point_num = gps_point_num
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.gps_alt = gps_alt
        self.gps_dop = gps_dop

    def check_for_image(self, image_list):
        index = -1
        try:
            index = image_list.index(str(self.gps_point_num) + IMAGE_FILE_EXT)
            self.image_name = image_list[index]
        except ValueError as err:
            self.image_name = IMAGE_DNE 
        
        return
        
    def format_gps_data(self):
        return {
            'latitude': self.gps_lat,
            'longitude': self.gps_long,
            'altitude': self.gps_alt,
            'dop': self.gps_dop
        }


# Insertion point
if __name__ == '__main__':
    # Indicate beginning of module
    print()
    print('#'*75 + '\n')
    print('Starting image parsing module...\n')
    print('#'*75 + '\n')

    parser = argparse.ArgumentParser(description='Image Parsing Module')
    parser.add_argument('images_folder', metavar='folder', type=str, default=Path('DataTest', 'GrassPatch01', 'Images'), help='Path to images')
    parser.add_argument('output_folder', metavar='folder', type=str, default=Path('DataTest', 'GrassPatch01', 'Output'), help='Path to output data')

    args = parser.parse_args()

    # Begin Image Parsing Module
    validate_args(args.images_folder, args.gps_data_file)

    transfer_images(args.images_folder)

    add_config_file()

    gps_data_points = read_gps_data(args.gps_data_file)

    gps_image_matches = match_gps_to_images(gps_data_points)

    create_gps_overrides(gps_image_matches)
