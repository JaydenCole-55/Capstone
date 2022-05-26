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
import subprocess
from pathlib import Path


###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
IMAGE_NAME = 'puttfromthesky2'
CONTAINER_NAME = 'PFS_1'

DOCKER_FILE_PATH = "bin/plot_tracks"
LOCAL_FILE_PATH = "OpenSfM/" + DOCKER_FILE_PATH


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def transfer_file_to_docker():
    # Indicate beginning of module
    print()
    print('#'*75 + '\n')
    print('Copying file to docker...\n')
    print('#'*75 + '\n')

    #   1. Start Docker Container
    print("Starting container")
    #subprocess.check_output(['docker', 'run', '-it', '-d', '--name', CONTAINER_NAME, IMAGE_NAME + ':latest'])

    # Find container ID from container name
    output = str(subprocess.check_output(['docker', 'container', 'ls', '-a', '-f', "name=" + CONTAINER_NAME]))

    containers_list = output.split(sep='\\n')

    for container in containers_list:
        if CONTAINER_NAME in container:
            container_ID = container.split()[0]

    #   2. Check if the docker has the file already, if so, remove it
    output = subprocess.check_output(['docker', 'exec', CONTAINER_NAME, 'sh', '-c', 'if [ -f ' + DOCKER_FILE_PATH + ' ] ; then rm ' + DOCKER_FILE_PATH + ' ; fi'])

    #   3. Copy file to the container
    output = subprocess.check_output(['docker', 'cp', Path(LOCAL_FILE_PATH) , container_ID + ':/source/OpenSfM/' + DOCKER_FILE_PATH])

    return 0


# Insertion point
if __name__ == '__main__':
    transfer_file_to_docker()
