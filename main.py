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
#   1. Run Metashape pipeline
#   2. Run the slope model generation script
#
###################################################################################################
import argparse

from pathlib import Path
from slope_model_generation import generate_slope_map

STORE_GRADIENTS = True
READ_GRADIENTS = True

def run_pipeline(input_folder, output_folder):
    ########################################
    #
    # Run the pipeline
    #
    ########################################
    # 1. Run Metashape Pipeline

    # 2. Run the slope model generation script
    generate_slope_map(output_folder, STORE_GRADIENTS, not READ_GRADIENTS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full image processing pipeline')
    parser.add_argument('data_folder', metavar='folder', type=str, default=Path('Data', 'EagleQuest_hole0'), help='Path to input folder')

    args = parser.parse_args()

    input_folder = Path(args.data_folder, "inputs")
    output_folder = Path(args.data_folder, "output")

    run_pipeline(input_folder, output_folder)
