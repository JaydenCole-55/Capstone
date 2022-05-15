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
import os
from pathlib import Path

from image_parsing import image_parsing
from image_processing import process_images
from slope_model_generation import orchestration

PLY_FILE = "merged.ply"

def run_pipeline(input_folder, gps_file, output_folder):
    ########################################
    #
    # Run the pipeline
    #
    ########################################
    
    # 1. Run the image and GPS combination data
    image_parsing(input_folder, gps_file)

    # 2. Run the image processing
    process_images(input_folder, output_folder)

    # 3. Run the slope model generation script
    orchestration(Path(output_folder, PLY_FILE))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full image processing pipeline')
    parser.add_argument('images_folder', metavar='folder', type=str, default=Path('DataTest', 'PICS for GPS-20220412T022518Z-001', 'input', 'images'      ), help='Path to images')
    parser.add_argument('gps_data',      metavar='file',   type=str, default=Path('DataTest', 'PICS for GPS-20220412T022518Z-001', 'input', 'GPS_data.txt'), help='Path to gps_data file')
    parser.add_argument('output_folder', metavar='folder', type=str, default=Path('DataTest', 'PICS for GPS-20220412T022518Z-001', 'output'               ), help='Path to output file')

    args = parser.parse_args()

    run_pipeline(args.images_folder, args.gps_data, args.output_folder)
