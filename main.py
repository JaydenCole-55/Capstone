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


def run_pipeline(input_folder, output_folder):
    ########################################
    #
    # Run the pipeline
    #
    ########################################
    
    # 1. Run the image and GPS combination data


    # 2. Run the image processing

    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full image processing pipeline')
    parser.add_argument('input_folder', metavar='folder', type=str, default=Path('Data', '2022-02-26_GrassPatch01', 'Hole01', 'input'), help='Path to input data folder')
    parser.add_argument('output_folder', metavar='folder', type=str, default=Path('Data', '2022-02-26_GrassPatch01', 'Hole01', 'output'), help='Path to input data folder')

    args = parser.parse_args()

    run_pipeline(args.input_folder, args.output_folder)