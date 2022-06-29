###################################################################################################
#
#                               SLOPE MODEL GENERATION MODULE TESTS
#
#
# Testing funcitonalities for the slope generation module that are not desirable in the final
# pipeline
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-06-07
#
# Algorithm:
#   1. Will vary by the functionality used
#
###################################################################################################
import math
import argparse
import numpy as np

from tqdm import tqdm
from pathlib import Path
from slope_model_generation import read_ply_file


###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
PLY_FILE_PATH = Path('Data', 'westwood_plateua_practise_green','WWP_1_highest_quality.ply')

from slope_model_generation import GRID_SIZE_X, GRID_SIZE_Y

X_VIEWING_DENSITY = 20
Y_VIEWING_DENSITY = 20

SLOPES_FILE = "slope_visulaizations.csv"


###################################################################################################
#
#                                            CLASSES
#
###################################################################################################
from slope_model_generation import Surface_Data

###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def calculate_plane_of_best_fit(indicies, s_data):
    # Preallocate memory
    xs = np.zeros(len(indicies))
    ys = np.zeros(len(indicies))
    zs = np.zeros(len(indicies))

    # Store the data points of interest
    counter = 0
    for index in indicies:
        xs[counter] = s_data.x[index]
        ys[counter] = s_data.y[index]
        zs[counter] = s_data.z[index]
        counter+=1

    # Fit a 2D plane to the data
    tmp_A = []
    tmp_b = []
    for i in range(len(indicies)):
        tmp_A.append([xs[i], ys[i], 1])
        tmp_b.append(zs[i])
    b = np.matrix(tmp_b).T
    A = np.matrix(tmp_A)
    try:
        fit = (A.T * A).I * A.T * b
    except Exception as e:
        # TODO: sometimes there are multiples of the same point in the ply file,
        # for now, return a null gradient - Preferably ply file creation would check for no double
        # points
        print("Cannot compute a gradient in a grid section due to multiples of the same point")

        return None
    
    return fit


def store_new_ply_points(ply_file):
    # Read in data
    data = read_ply_file(ply_file)

    # Now that the data is collected, create a GRID_SIZE_X x GRID_SIZE_Y grid from min & max x and y points
    max_x = max(data.x)
    min_x = min(data.x)
    max_y = max(data.y)
    min_y = min(data.y)

    # Determine grid boxes dimensions
    length_x = max_x - min_x
    step_x = length_x/GRID_SIZE_X

    length_y = max_y - min_y
    step_y = length_y/GRID_SIZE_Y

    # Write the gradients to a text file
    temp_ply_file = open(SLOPES_FILE, "w")

    # Calculate planes of best fit to the data
    for i in tqdm(range(GRID_SIZE_Y), desc="Y axis (NS) calculations"):
        for j in tqdm(range(GRID_SIZE_X), desc="X axis (EW) calculations", leave=False):
            # Determine grid area x and y selections
            x_start  = min_x + step_x*j
            x_finish = min_x + step_x*(j+1)
            y_start  = min_y + step_y*i
            y_finish = min_y + step_y*(i+1)

            # Find all points within this grid area
            indicies = list(filter(lambda k: data.x[k] >= x_start and data.x[k] <= x_finish and data.y[k] >= y_start and data.y[k] <= y_finish, range(len(data.x))))

            fit = True
            if len(indicies) <= 1:
                # No gradient can be given for a grid area that contains less than two points
                fit = False
            else:
                # Find a vector that averages the slopes of the grid area points
                plane_of_best_fit = calculate_plane_of_best_fit(indicies, data)

            # Add visualization of the plane of best fit here
            x_vals = np.linspace(x_start, x_finish, X_VIEWING_DENSITY)
            y_vals = np.linspace(y_start, y_finish, Y_VIEWING_DENSITY)

            for x in x_vals:
                for y in y_vals:
                    if fit:
                        z = np.squeeze(np.asarray(plane_of_best_fit[0]*x +  plane_of_best_fit[1]*y + plane_of_best_fit[2]))
                    else:
                        z = 0

                    temp_ply_file.write(str(np.round(x, 4)) + "," + str(np.round(y, 4)) + "," + str(np.round(z, 4)) + "\n")

    temp_ply_file.close()

    return data


def create_new_ply_file(data):
    ###################################
    #
    # Create a new ply file incorporating the old and new ply points
    #
    ###################################

    # From old ply file find number of points
    old_num_pts = len(data.x)
    
    # Then add the number of new points
    new_num_pts = old_num_pts + X_VIEWING_DENSITY*Y_VIEWING_DENSITY*GRID_SIZE_X*GRID_SIZE_Y

    # Then write header
    visualization_file = open("slope_visualizations.ply", "w")
    visualization_file.write("ply\n")
    visualization_file.write("format ascii 1.0\n")
    visualization_file.write("element vertex " + str(new_num_pts) + "\n")
    visualization_file.write("property float x\n")
    visualization_file.write("property float y\n")
    visualization_file.write("property float z\n")
    visualization_file.write("property float nx\n")
    visualization_file.write("property float ny\n")
    visualization_file.write("property float nz\n")
    visualization_file.write("property uchar diffuse_red\n")
    visualization_file.write("property uchar diffuse_green\n")
    visualization_file.write("property uchar diffuse_blue\n")
    visualization_file.write("property uchar class\n")
    visualization_file.write("end header\n")

    # Then transfer points from both source files to the new file

    # Transfer data from old file, pts will be green
    for i in range(len(data.x)):
        visualization_file.write(str(data.x[i]) + " " + str(data.y[i]) + " " + str(data.z[i]) + " 0 0 0 0 255 0 0\n")

    # Transfer data from visualization file
    with open(SLOPES_FILE, 'r') as slope_file:
        for line in slope_file.readlines():
            x, y, z = line.split(",")
            visualization_file.write(x + " " + y + " " + z[0:-1] + " 0 0 0 255 0 0 0\n")

    visualization_file.close()

    return data


def visualize_slopes(data_ply_file):
    ##############################################
    #
    # Creates a new ply file with the calculated 
    # slopes visualized
    #
    ##############################################
    if True:
        data = store_new_ply_points(data_ply_file)
    else:
        data = read_ply_file(data_ply_file)

    create_new_ply_file(data)


if __name__ == '__main__':
    # Read in arguments
    parser = argparse.ArgumentParser(description='Find slopes from a ply file')
    parser.add_argument('--ply_file', metavar='file', type=str, default=PLY_FILE_PATH, help='Ply file path')

    args = parser.parse_args()

    visualize_slopes(args.ply_file)