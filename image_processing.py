###################################################################################################
#
#                                  IMAGE PROCESSING MODULE
#
#
# Creates a ply file of verticies from a set of images
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-03-23
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
import subprocess
from pathlib import Path
import argparse

from image_parsing import CONFIG_YAML

###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
IMAGE_NAME = 'puttfromthesky2'
CONTAINER_NAME = 'PFS_1'
PROCESSING_FOLDER = 'green'
PLY_FILE = PROCESSING_FOLDER + '/undistorted/depthmaps/merged.ply'
DOCKER_FILE_PATH = './OpenSfM/'

IMAGE_PATH = 'images'
EXIF_JSON = 'exif_overrides.json'

###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def process_images(host_input_folder, host_destination_folder):
    # Indicate beginning of module
    print()
    print('#'*75 + '\n')
    print('Starting image processing module...\n')
    print('#'*75 + '\n')

    # Ensure output directory exists
    os.makedirs(host_destination_folder, exist_ok=True)

    #   1. Create Docker Image (if not already built)
    print("Building Docker image")
    #subprocess.check_output(['docker', 'build', '-t', IMAGE_NAME, DOCKER_FILE_PATH])

    #   2. Create and Start Docker Container
    print("Starting container")
    subprocess.check_output(['docker', 'run', '-it', '-d', '--name', CONTAINER_NAME, IMAGE_NAME + ':latest'])

    # Find container ID from container name
    output = str(subprocess.check_output(['docker', 'container', 'ls', '-a', '-f', "name=" + CONTAINER_NAME]))

    containers_list = output.split(sep='\\n')

    for container in containers_list:
        if CONTAINER_NAME in container:
            container_ID = container.split()[0]

    #   3. Copy image data to Docker Image
    print('Copying images to container')
    output = subprocess.check_output(['docker', 'exec', CONTAINER_NAME, 'mkdir', 'data/' + PROCESSING_FOLDER])
    output = subprocess.check_output(['docker', 'cp', Path(host_input_folder, IMAGE_PATH) , container_ID + ':/source/OpenSfM/data/' + PROCESSING_FOLDER])
    output = subprocess.check_output(['docker', 'cp', Path(host_input_folder, EXIF_JSON),   container_ID + ':/source/OpenSfM/data/' + PROCESSING_FOLDER])
    output = subprocess.check_output(['docker', 'cp', Path(host_input_folder, CONFIG_YAML), container_ID + ':/source/OpenSfM/data/' + PROCESSING_FOLDER])

    #   4. Run the image processing pipeline in the Docker Image
    print('Running processing pipeline... this can take 30-40 minutes')
    subprocess.check_output(['docker', 'exec', '-it',  CONTAINER_NAME, 'sh', '-c', 'bin/opensfm_run_all data/' + PROCESSING_FOLDER, ';', 'mkdir', 'done' ])

    #   5. Copy results from Docker to host machine
    print('Collecting output from processing pipeline')
    output = subprocess.check_output(['docker', 'cp', container_ID + ':/source/OpenSfM/data/' + PLY_FILE, host_destination_folder])

    # Uncomment to copy whole data folder from docker image
    #output = subprocess.check_output(['docker', 'cp', container_ID + ':/source/OpenSfM/data/green/', host_destination_folder])

    #   6. Delete container from docker
    output = subprocess.check_output(['docker', 'container', 'stop', container_ID])
    output = subprocess.check_output(['docker', 'container', 'rm', container_ID])
    print('Container deleted, image processing completed\n\n')

    return 0


# Insertion point
if __name__ == '__main__':
    # Run an example processing pipeline
    parser = argparse.ArgumentParser(description='Image Processing Module')
    parser.add_argument('-i', '--images_folder', metavar='folder', type=str, default=Path('imageData'), help='Path to input folder')
    parser.add_argument('-o', '--output_folder', metavar='file', type=str, default=Path('DataTest', 'GPS_Data_test', 'output'), help='Path to gps_data file')

    args = parser.parse_args()

    process_images(args.images_folder, args.output_folder)
