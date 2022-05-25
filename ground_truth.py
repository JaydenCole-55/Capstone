###################################################################################################
#
#                                  GROUND TRUTH MODULE
#
#
# Reads in a CSV file containing ground truth slope data and creates green map
# The program will be data specific and mainly manually done. 
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-05-21
#
###################################################################################################
from configparser import Interpolation
import math
import copy
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
X = 0
Y = 1
Z = 2
GRID_SIZE_X = 14
GRID_SIZE_Y = 10
POS_DIR = 'U'
DATA_POINTS = 81

###################################################################################################
#
#                                            CLASSES
#
###################################################################################################
class Data_Element(object):
    ################################
    # Read in data from file
    ################################
    def __init__(self, line):

        values = line.split(",")

        # File format: Measurement Number,EW Slope,Down/Up,NS Slope,Down/Up,Column Number
        # Read file line in
        self.data_point = int(values[0])
        self.EW_mag = float(values[1])
        self.EW_dir = 1 if values[2] == POS_DIR else -1
        self.NS_mag = float(values[3])
        self.NS_dir = 1 if values[4] == POS_DIR else -1
        self.col = int(values[5])

    def compute_vector_mag(self):
        return np.sqrt(self.EW_mag ** 2 + self.NS_mag ** 2)
        
    def compute_vector_dir(self):
        # Computes theta where theta = 0 is directly west and theta = 90 is directly south
        if self.EW_mag == 0:
            return self.NS_dir * -1 * (np.pi/2)
        else:
            return np.arctan((self.NS_dir*self.NS_mag) / (self.EW_dir*self.EW_mag))

    def get_EW_vect(self):
        # Returns the EW vector where west is positive
        return self.EW_mag * self.EW_dir

    def get_NS_vect(self):
        # Returns the NS vector where south is positive
        return self.NS_mag * self.NS_dir


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def read_csv_file(csv_file):
    ################################
    # 
    # Read in a csv file of a surface mesh, store that data into memory
    # Input: Absolute File location (str)
    # Output: Structure of ply file data
    # 
    ################################
    print('Reading file: ', csv_file)
    in_file_header = True

    i = 0
    data = []

    with open(csv_file) as csvFile:
        # Iterate through each line of the file storing the data
        for line in csvFile:

            # skip the first line (it is a header)
            if i == 0 and in_file_header:
                i+=1
                continue
            else:
                # Parse file body for x, y, and z data values
                data.append(Data_Element(line))
                i+=1

    print('Finished reading file\n')
    return data


def create_green_grid(data_points):
    #######################################
    #
    # Plots the green slopes in a quiver plot
    #
    # Input: 2D array of with each element defining the gradient of a section of the green
    # Returns: None
    # Output: Quiver Plot
    #
    ######################################

    green_grid = [ [0]*GRID_SIZE_X for _ in range(GRID_SIZE_Y)]
    green_dir_grid = [ [0]*GRID_SIZE_X for _ in range(GRID_SIZE_Y)]
    green_point_grid = [ [0]*GRID_SIZE_X for _ in range(GRID_SIZE_Y)]


    data_point = 0

    # Add column 0 points 
    green_grid[5][0] = data_points[data_point].compute_vector_mag()
    green_dir_grid[5][0] = data_points[data_point].compute_vector_dir()
    green_point_grid[5][0] = data_points[data_point]
    data_point+=1

    # Add column 1 points 
    for i in range(6):
        green_grid[i+2][1] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+2][1] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+2][1] = data_points[data_point + i]
    data_point+=6

    # Add column 2 points 
    for i in range(9):
        green_grid[i][2] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i][2] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i][2] = data_points[data_point + i]
    data_point+=9

    # Add column 3 points 
    for i in range(9):
        green_grid[i][3] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i][3] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i][3] = data_points[data_point + i]
    data_point+=9

    # Add column 4 points 
    for i in range(9):
        green_grid[i][4] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i][4] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i][4] = data_points[data_point + i]
    data_point+=9

    # Add column 5 points 
    for i in range(9):
        green_grid[i][5] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i][5] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i][5] = data_points[data_point + i]
    data_point+=9

    # Add column 6 points -- done manually due to weird skip 
    green_grid[1][6] = data_points[data_point + 0].compute_vector_mag()
    green_grid[2][6] = data_points[data_point + 1].compute_vector_mag()
    # Skip data point 3
    green_grid[4][6] = data_points[data_point + 2].compute_vector_mag()
    green_grid[5][6] = data_points[data_point + 3].compute_vector_mag()
    green_grid[6][6] = data_points[data_point + 4].compute_vector_mag()
    green_grid[7][6] = data_points[data_point + 5].compute_vector_mag()
    green_grid[8][6] = data_points[data_point + 6].compute_vector_mag()

    # Direction
    green_dir_grid[1][6] = data_points[data_point + 0].compute_vector_dir()
    green_dir_grid[2][6] = data_points[data_point + 1].compute_vector_dir()
    # Skip data point 3
    green_dir_grid[4][6] = data_points[data_point + 2].compute_vector_dir()
    green_dir_grid[5][6] = data_points[data_point + 3].compute_vector_dir()
    green_dir_grid[6][6] = data_points[data_point + 4].compute_vector_dir()
    green_dir_grid[7][6] = data_points[data_point + 5].compute_vector_dir()
    green_dir_grid[8][6] = data_points[data_point + 6].compute_vector_dir()

    # Data Points
    green_point_grid[1][6] = data_points[data_point + 0]
    green_point_grid[2][6] = data_points[data_point + 1]
    # Skip data point 3
    green_point_grid[4][6] = data_points[data_point + 2]
    green_point_grid[5][6] = data_points[data_point + 3]
    green_point_grid[6][6] = data_points[data_point + 4]
    green_point_grid[7][6] = data_points[data_point + 5]
    green_point_grid[8][6] = data_points[data_point + 6]
    data_point+=7

    # Add column 7 points 
    for i in range(6):
        green_grid[i+2][7] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+2][7] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+2][7] = data_points[data_point + i]
    data_point+=6

    # Add column 8 points 
    for i in range(5):
        green_grid[i+4][8] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+4][8] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+4][8] = data_points[data_point + i]
    data_point+=5

    # Add column 9 points 
    for i in range(5):
        green_grid[i+4][9] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+4][9] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+4][9] = data_points[data_point + i]
    data_point+=5

    # Add column 10 points 
    for i in range(5):
        green_grid[i+5][10] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+5][10] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+5][10] = data_points[data_point + i]
    data_point+=5

    # Add column 11 points 
    for i in range(5):
        green_grid[i+5][11] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+5][11] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+5][11] = data_points[data_point + i]
    data_point+=5

    # Add column 12 points 
    for i in range(4):
        green_grid[i+6][12] = data_points[data_point + i].compute_vector_mag()
        green_dir_grid[i+6][12] = data_points[data_point + i].compute_vector_dir()
        green_point_grid[i+6][12] = data_points[data_point + i]
    data_point+=4

    # Add column 13 points 
    green_grid[7][13] = data_points[data_point].compute_vector_mag()
    green_dir_grid[7][13] = data_points[data_point].compute_vector_dir()
    green_point_grid[7][13] = data_points[data_point]

    #print_grid(green_grid, '{:6.2f}')
    #print()
    #print()
    #print_grid(green_dir_grid, '{:5.2f}  ')

    return [green_grid, green_dir_grid, green_point_grid]


def print_grid(array_2d, formatting):
    #######################################
    #
    # Prints a 2D array as a grid
    #
    ######################################
    for row in array_2d:
        print_row = "";
        for val in row:
            print_row += formatting.format(val)
        print(print_row)

    return

def normalize(X, Y):
    #######################################
    #
    # Normalize the X and Y vectors for quiver plot
    #
    ######################################
    qX = []
    qY = []

    for i in range(GRID_SIZE_Y):
        qx = []
        qy = []
        for j in range(GRID_SIZE_X):
            xVal = X[i][j]
            yVal = Y[i][j]
            if (xVal == 0 and yVal == 0):
                qx.append(0)
                qy.append(0)
            else:
                qx.append(xVal / np.sqrt(xVal**2 + yVal**2))
                qy.append(yVal / np.sqrt(xVal**2 + yVal**2))

        qX.append(qx)
        qY.append(qy)

    return [qX, qY]


def plot_green(slope_mag, slope_dir, data):
    #######################################
    #
    # Plots the green slopes in a quiver plot
    #
    # Input: 2D array of with each element defining a grid element
    # Returns: None
    # Output: Heat map and quiver plot
    #
    ######################################

    # Define grid points
    xPoints = np.linspace(0, GRID_SIZE_X, GRID_SIZE_X, False)
    yPoints = np.linspace(0, GRID_SIZE_Y, GRID_SIZE_Y, False)
    xx = []
    yy = []
    mag = []

    # Map gradients to X and Y slopes
    for i in range(GRID_SIZE_Y):
        magArr = []
        xRow = []
        yRow = []
        for j in range(GRID_SIZE_X):
            if (data[i][j] == 0):
                magArr.append(0)
                xRow.append(0)
                yRow.append(0)
            else:
                magArr.append(data[i][j].compute_vector_mag())
                xRow.append(data[i][j].get_EW_vect())
                yRow.append(data[i][j].get_NS_vect())
        mag.append(magArr)
        xx.append(xRow)
        yy.append(yRow)

    # Normalize arrows for quiver plot
    [qX, qY] = normalize(xx, yy)

    # Plot
    plt.quiver(xPoints, yPoints, qX, qY, scale=5, scale_units="inches")
    plt.imshow(mag, cmap="jet", interpolation="hanning")
    plt.colorbar()

    # Interpolcation methods = [None, 'none', 'nearest', 'bilinear', 'bicubic', 
    # 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
    # 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    plt.show()
    

    return

def orchestration(csv_file):

    data = read_csv_file(csv_file)

    [mag, theta, point] = create_green_grid(data)

    plot_green(mag, theta, point)
    

# Insertion point
if __name__ == '__main__':
    # Read in arguments
    parser = argparse.ArgumentParser(description='Find green map from ground truth data, formatted in csv file')
    parser.add_argument('csv_file', metavar='file', type=str, default=Path('GroundTruth', 'WWP_GreenTruth.csv'), help='Path to csv file')

    args = parser.parse_args()

    orchestration(args.csv_file)
