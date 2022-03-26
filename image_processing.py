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


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def process_images(host_images_folder, host_destination_folder):
    image_name = 'puttfromthesky'
    container_name = 'PFS_1'
    processing_folder = 'green'
    ply_file = processing_folder + "/undistorted/depthmaps/merged.ply"

    DOCKER_FILE_PATH = './OpenSfM/'

    # Ensure output directory exists
    os.makedirs(host_destination_folder, exist_ok=True)

    #   1. Create Docker Image (if not already built)
    print("Building Docker image")
    subprocess.check_output(['docker', 'build', '-t', image_name, DOCKER_FILE_PATH])

    #   2. Create and Start Docker Container
    print("Starting container")
    subprocess.check_output(['docker', 'run', '-it', '-d', '--name', container_name, image_name + ':latest'])

    # Find container ID from container name
    output = str(subprocess.check_output(['docker', 'container', 'ls', '-a', '-f', "name="+container_name]))

    containers_list = output.split(sep='\\n')

    for container in containers_list:
        if container_name in container:
            container_ID = container.split()[0]

    #   3. Copy image data to Docker Image
    print('Copying images to container')
    output = subprocess.check_output(['docker', 'exec', container_name, 'mkdir', 'data/' + processing_folder])
    output = subprocess.check_output(['docker', 'cp', host_images_folder, container_ID + ':/source/OpenSfM/data/' + processing_folder])

    #   4. Run the image processing pipeline in the Docker Image
    print('Running processing pipeline')
    subprocess.check_output(['docker', 'exec', '-it',  container_name, 'sh', '-c', 'bin/opensfm_run_all data/' + processing_folder, ';', 'mkdir', 'done' ])

    #   5. Copy results from Docker to host machine
    print('Collecting output from processing pipeline')
    output = subprocess.check_output(['docker', 'cp', container_ID + ':/source/OpenSfM/data/' + ply_file, host_destination_folder])

    #   6. Delete container from docker
    output = subprocess.check_output(['docker', 'container', 'stop', container_ID])
    output = subprocess.check_output(['docker', 'container', 'rm', container_ID])
    print('Container deleted, image processing completed\n\n')

    return 0


# Insertion point
if __name__ == '__main__':
    # Run an example processing pipeline
    input_images_path = Path("./Data/2022-02-26_GrassPatch01/Hole01/images")
    output_data_path  = Path("./processedData/2022-02-26_GrassPatch01/Hole01/")

    process_images(input_images_path, output_data_path)
