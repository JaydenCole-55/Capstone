###################################################################################################
#
#                                  RUN ALL THE IMAGE PROCESSING SCRIPTS
#
#
# Runs the image processing pipeline from images and GPS file to slope map.
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-03-29
#
# Algorithm:
#   1. Run the Compiling GPS and Image data script
#   2. Run the image processing script
#   3. Run the slope model generation script
#
###################################################################################################
import argparse
from pathlib import Path
import os

PLY_FILE = "/merged.ply" # Needs to be fixed relative to output folder


def run_pipeline(input_folder, gps_file, output_folder):
    ########################################
    #
    # Run the pipeline
    #
    ########################################
    
    # 1. Run the image and GPS combination data
    os.system("image_parsing.py " + input_folder + " " + gps_file)

    # 2. Run the image processing
    os.system("image_processing.py " + input_folder + " " + output_folder)

    # 3. Run the slope model generation script
    os.system("slope_model_generation.py " + output_folder + "/merged.ply")

    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full image processing pipeline')
    parser.add_argument('images_folder', metavar='folder', type=str, default=Path('DataTest', 'GrassPatch01', 'Images'), help='Path to images')
    parser.add_argument('gps_data', metavar='file', type=str, default=Path('DataTest', 'GrassPatch01', 'gps_data.txt'), help='Path to gps_data file')
    parser.add_argument('output_folder', metavar='folder', type=str, default=Path('DataTest', 'GrassPatch01', 'Output'), help='Path to output data')

    args = parser.parse_args()

    run_pipeline(args.images_folder, args.gps_data, args.output_folder)