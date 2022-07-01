###################################################################################################
#
#                                  SLOPE MODEL GENERATION MODULE
#
#
# Generates a 2D slope map from a set of verticies in a ply file
# Authors: Jayden Cole & Ryan Stolys
# Creation date: 2022-02-26
#
# Algorithm:
#   1. Read in ply file
#   2. Calculate grid
#   3. Calculate slope within grid
#   4. Output graphical interpretation of the slopes on the green
#
###################################################################################################
import copy
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path
from sklearn import linear_model

###################################################################################################
#
#                                            CONSTANTS
#
###################################################################################################
X = 0
Y = 1
Z = 2

GRID_SIZE_X = 4
GRID_SIZE_Y = 4

GRADIENT_FILE = "grid_vector.txt"
PLY_FILE = "steady_x_increasing.ply"

X_UNIT_VECTOR = np.array([1, 0, 0])
Y_UNIT_VECTOR = np.array([0, 1, 0])

###################################################################################################
#
#                                            CLASSES
#
###################################################################################################
class Surface_Data(object):
    ################################
    #
    # Surface data storage object
    #
    ################################
    def __init__(self, num_verticies):

        # Allocate memory for vertex data
        self.x       = np.zeros(num_verticies)
        self.y       = np.zeros(num_verticies)
        self.z       = np.zeros(num_verticies)


###################################################################################################
#
#                                            FUNCTIONS
#
###################################################################################################
def read_ply_file(ply_file):
    ################################
    # 
    # Read in a ply file of a surface mesh, store that data into memory
    # Input: Absolute File location (str)
    # Output: Structure of ply file data
    # 
    ################################
    print('Reading file: ', ply_file)
    in_file_header = True

    i = 0
    properties = []

    with open(ply_file) as plyFile:
        # Iterate through each line of the file storing the data
        for line in plyFile:

            # Parse information from file header
            if in_file_header:
                if 'end_header' in line:
                    in_file_header = False
                    s_data = Surface_Data(num_verticies)

                elif 'element' in line and 'vertex' in line:
                    num_verticies = int(line.split()[2])

                elif 'property' in line:
                    # Determine ply property ordering
                    property_name = line.split()[2]
                    properties.append(property_name)

                continue
            else:
                # Parse file body for x, y, and z data values
                if i < num_verticies:
                    s_data.x[i] = line.split()[properties.index("x")]
                    s_data.y[i] = line.split()[properties.index("y")]
                    s_data.z[i] = line.split()[properties.index("z")]

                    i+=1

    print('Finished reading file\n')
    return s_data


def calculate_gradient(indicies, s_data):
    #######################################
    #
    # Calculates the slope of the given indicies from the most top left corner point
    #
    # Input: list of indicies (ints), the vertex data object, grid area top left corner
    # Returns: Vector sum (tuple as (x, y, z))
    #
    ######################################

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

    xs = np.transpose(np.array(xs))
    ys = np.transpose(np.array(ys))

    # Fit a 2D plane to the data
    XY_data = np.zeros([len(xs), 2])
    for i in range(len(xs)):
        XY_data[i][0] = xs[i]
        XY_data[i][1] = ys[i]

    Z_data = zs

    # Fit plane to data
    reg = linear_model.LinearRegression().fit(XY_data, Z_data)

    # Plane of best fit Ax + By + C = z
    A = reg.coef_[0]
    B = reg.coef_[1]
    C = reg.intercept_

    # Get normal to plane through cross product of two vectors in plane
    z_of_xy_00 = A*0 + B*0 + C
    z_of_xy_10 = A*1 + B*0 + C
    z_of_xy_01 = A*0 + B*1 + C

    p00z = np.array([0, 0, z_of_xy_00])
    p10z = np.array([1, 0, z_of_xy_10])
    p01z = np.array([0, 1, z_of_xy_01])

    v1 = p10z - p00z
    v2 = p01z - p00z

    pobf_normal_vector = np.cross(v1, v2)

    # Get 2 points on pobf that are x, y of the normal vector apart
    z_of_normal_xy =  A*pobf_normal_vector[0] + B*pobf_normal_vector[1] + C
    pxyz = np.array([pobf_normal_vector[0], pobf_normal_vector[1], z_of_normal_xy])

    # The gradient is the vector between this pxyz and p00z
    gradient = p00z - pxyz

    # Normalize the gradient wrt its x and y components (as long as it is not 0)
    if not np.array_equal(gradient, np.zeros(3)):
        gradient = gradient / np.sqrt((gradient[X])**2 + (gradient[Y])**2)

    return -1 * gradient


def create_gradient_grid(ply_file, store_gradients, read_gradients):
    # Display output
    print()
    print('#'*75 + '\n')
    print('Starting slope generation module...\n')
    print('#'*75 + '\n')

    # Allocate grid vector memory
    lst = np.zeros(GRID_SIZE_X)
    intermediate_step = list(zip(lst, lst, lst))
    grid_vector = []
    for i in range(GRID_SIZE_Y):
        grid_vector.append(copy.deepcopy(intermediate_step)) 
    
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

    # Determine if to read gradients from memory or to calculate them
    if read_gradients:
        print("Reading Gradients from file: " + GRADIENT_FILE)
        file_handle = open(GRADIENT_FILE, "r")
        for i in range(GRID_SIZE_X):
            for j in range(GRID_SIZE_Y):
                grid_vector[i][j] = tuple(np.asarray(file_handle.readline()[:-1].split(',')).astype(float))

        file_handle.close()

    else:
        # Go through each grid area and find average slope
        for i in tqdm(range(GRID_SIZE_Y), desc="Y axis (NS) calculations"):
            for j in tqdm(range(GRID_SIZE_X), desc="X axis (EW) calculations", leave=False):
                # Determine grid area x and y selections
                x_start  = min_x + step_x*j
                x_finish = min_x + step_x*(j+1)
                y_start  = min_y + step_y*i
                y_finish = min_y + step_y*(i+1)

                # Find all points within this grid area
                indicies = list(filter(lambda k: data.x[k] >= x_start and data.x[k] <= x_finish and data.y[k] >= y_start and data.y[k] <= y_finish, range(len(data.x))))

                if len(indicies) <= 1:
                    # No gradient can be given for a grid area that contains less than two points
                    continue
                else:
                    # Find a vector that averages the slopes of the grid area points
                    grid_vector[i][j] = calculate_gradient(indicies, data)

        if store_gradients:
            # Write the gradients to a text file
            file_handle = open(GRADIENT_FILE, "w")
            for i in range(GRID_SIZE_X):
                for j in range(GRID_SIZE_Y):

                    if not (i == 0 and j == 0):
                        file_handle.write('\n')

                    file_handle.write(str(grid_vector[i][j][X]) + ',')
                    file_handle.write(str(grid_vector[i][j][Y]) + ',')
                    file_handle.write(str(grid_vector[i][j][Z]))

            file_handle.close()

    return grid_vector


def plot_green(data):
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
    xx = []
    yy = []
    mag = []

    # Map gradients to X and Y slopes
    for i in range(GRID_SIZE_Y-1, -1, -1):
        magArr = []
        xRow = []
        yRow = []
        for j in range(GRID_SIZE_X):
            magArr.append(abs(data[i][j][Z]) * 100) # Convert rise/run to degrees (Eg. 0.01 rise/1 run = 1 degree)
            xRow.append(data[i][j][X])
            yRow.append(-1*data[i][j][Y]) # Y positive axis is downward, flip to get arrows in correct direction
        mag.append(magArr)
        xx.append(xRow)
        yy.append(yRow)

    # Plot
    plt.quiver(xx, yy, scale=2, scale_units="xy", pivot="mid")
    plt.imshow(mag, cmap="jet", interpolation="hanning")
    plt.clim(0.0, 5.0)
    plt.colorbar()

    # Interpolcation methods = [None, 'none', 'nearest', 'bilinear', 'bicubic', 
    # 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
    # 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    plt.show()

    return


def generate_slope_map(output_folder, store_gradients, read_gradients):
    #######################################
    #
    # Calls all the functions needed to create greens map 
    #
    ######################################
    ply_file = Path(output_folder, PLY_FILE)

    gradient_grid = create_gradient_grid(ply_file, store_gradients, read_gradients)

    plot_green(gradient_grid)

    return


# Insertion point
if __name__ == '__main__':
    # Read in arguments
    parser = argparse.ArgumentParser(description='Find slopes from a ply file')
    parser.add_argument('data_folder', metavar='file', type=str, default=Path(), help='Data folder path')
    parser.add_argument('--store_gradients', action='store_true', help='Store calculated gradients to memory')
    parser.add_argument('--read_gradients', action='store_true', help='Get gradients from memory')

    args = parser.parse_args()

    generate_slope_map(args.data_folder, args.store_gradients, args.read_gradients)
