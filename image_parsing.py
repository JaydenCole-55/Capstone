###################################################################################################
#
#                                  IMAGE PARSING MODULE
#
#
# Moves images to appropriate folder, formats gps data from images 
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-03-26
#
# Algorithm:
#   1. Create Docker Image (if not already built)
#   2. Create and Start Docker Container
#   3. Copy image data to Docker Image
#   4. Run the image processing pipeline in the Docker Image
#   5. Copy results from Docker to host machine
#
###################################################################################################
import os
import json
from tkinter import image_names

###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def override_gps_location(gps_image_matches): # gps_image_matches: [GPS_IMAGE]
    exif_overrides = {}

    # Create JSON object
    for gps_image_match in gps_image_matches:
        exif_overrides[gps_image_match.image_name] = gps_image_match.format_gps_data()

    # Write JSON object to file
    with open('exif_overrides.json', 'w') as outfile:
        json.dump(exif_overrides, outfile)

    return 0

###################################################################################################
#
#                                            CLASSES
#
###################################################################################################
class GPS_IMAGE:
    def __init__ (self, image_name, gps_lat, gps_long, gps_alt, gps_dop):
        self.image_name = image_name
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.gps_alt = gps_alt
        self.gps_dop = gps_dop

    def format_gps_data(self):
        return {
            'latitude': self.gps_lat,
            'longitude': self.gps_long,
            'altitude': self.gps_alt,
            'dop': self.gps_dop
        }


# Insertion point
if __name__ == '__main__':
    # Read image directory 

    # Move images to image Data directory in correct format

    # Add config.yaml file

    # read gps location file

    # match gps locations to images 
    gps_image_matches = []
    gps_image_match = GPS_IMAGE("test.JPG", 52.51891, 13.40029, 27.0, 5.0) 
    gps_image_matches.append(gps_image_match)

    # Create exif_overrides file for gps location
    override_gps_location(gps_image_matches)
