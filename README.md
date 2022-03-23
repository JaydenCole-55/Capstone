# Capstone
SFU Engineering Science Capstone Project - 2022

## Modules
#### Image Parsing (IP)
* Import image files
* Read and parse files

#### Feature Detection and Matching (FDM)
* Feature dectection using SIFT
* Feature Matching using Lucas-Kanade

#### Point Cloud Generation (PCG)
* Sparse Reconstruction
* Dense Reconstruction

#### Slope Model Generation (SMG)
* Convert Mesh to slope model
* Generation Graphical Slope Model



## Requirements
* Python 3.10.2
* Docker Desktop 4.6.0 (only need docker CLI)

## Setup (Attempt 1)
* Create a volume on host machine using: `docker volume create ImageData`. This shoudl create a folder located at `/var/lib/docker/volumes/ImageData/_data` (May be different on Windows). Check using `docker volume inspect --format '{{ .Mountpoint }}' ImageData` or generally `docker volume inspect ImageData`
* Naviagte to OpenSfM folder. Create docker image (if not already built) using: `docker build -t puttfromsky .`
* Create docker container from image with volume using: `docker run -it -d --name PFS_1 -v ImageData:/source/OpenSfM/images puttfromsky`
* Run image processing pipeline using: `docker exec -it PFS_1 bin/opensfm_run_all images` (Format: docker exec -it _container_name_ _command_)
* Track down .ply file... 

## Setup (Attempt 2)
* Create Docker Image (if not already built)
    * Naviagte to OpenSfM folder
    * Create docker image  using: `docker build -t puttfromsky .` 
* Create and Start Docker Container
    * Run Command: `docker run -it -d --name PFS_1 puttfromsky:latest`
* Copy image data to docker image
    * Run Command: `docker cp ./imageData _containerId:/source/openSfM/data/green`
* Run the image processing pipeline
    * Run Command: `docker exec -it PFS_1 bin/opensfm_run_all images`
    * This can be adapted to only run one command at a time
* Copy results from docker to host machine
    * Run Command: `docker cp _containerId:/source/openSfM/data/green/undistored ./map`
    * Can be more specific with with files we want to copy back. Only care about .ply file

