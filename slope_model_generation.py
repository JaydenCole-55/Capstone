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
PLY_FILE_PATH = Path("green", "undistorted", "depthmaps", "steady_y_increasing-flat.ply")
#PLY_FILE_PATH = Path("green", "undistorted", "depthmaps", "flat.ply")
#PLY_FILE_PATH = Path("green", "undistorted", "depthmaps", "corners.ply")

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


def calculate_gradient(indicies, s_data, grid_location):
    #######################################
    #
    # Calculates the slope of the given indicies from the most top left corner point
    #
    # Input: list of indicies (ints), the vertex data object, grid area top left corner
    # Returns: Vector sum (tuple as (x, y, z))
    #
    ######################################

    # Determine location of grid area
    x_min = grid_location[0]
    y_min = grid_location[1]
    x_max = grid_location[2]
    y_max = grid_location[3]

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

    # Fit a 2D plane to the data - Old
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

        return (0, 0, 0)

    left_top     = [x_min, y_min, float(np.squeeze(np.array(x_min * fit[0] + y_min * fit[1] + fit[2])))]
    left_bottom  = [x_min, y_max, float(np.squeeze(np.array(x_min * fit[0] + y_max * fit[1] + fit[2])))]
    right_top    = [x_max, y_min, float(np.squeeze(np.array(x_max * fit[0] + y_min * fit[1] + fit[2])))]
    right_bottom = [x_max, y_max, float(np.squeeze(np.array(x_max * fit[0] + y_max * fit[1] + fit[2])))]

    # Eliminate floating point error through rounding
    left_bottom[2]  = round(left_bottom[2], 8)
    left_top[2]     = round(left_top[2], 8)
    right_bottom[2] = round(right_bottom[2], 8)
    right_top[2]    = round(right_top[2], 8)

    if left_top[2] - right_top[2] == 0 and left_top[2] - left_bottom[2] == 0:
        # Plane is flat, return no gradient vector
        return (0, 0, 0)
    elif left_top[2] - left_bottom[2] == 0:
        # Plane is flat in y direction, return x direction gradient
        gradient = np.subtract(left_top, right_top)
    elif left_top[2] - right_top[2] == 0:
        # Plane is flat in x direction, return y direction gradient
        gradient = np.subtract(left_top, left_bottom)
    elif abs(left_top[2] - right_bottom[2]) > abs(left_bottom[2] - right_top[2]):
        # Diagonal gradient (min_x, min_y <--> max_x, max_y)
        gradient = np.subtract(left_top, right_bottom)
    elif abs(left_bottom[2] - right_top[2]) > abs(left_top[2] - right_bottom[2]):
        # Diagonal gradient (min_x, max_y <--> min_x, max_y)
        gradient = np.subtract(left_bottom, right_top)
    else:
        # Should never end up here, print error for debugging, return (0, 0, 0)
        print("Calculated gradient did not fall into the 5 anticipate categories of gradient. Debug here")
        return (0, 0, 0)

    # Ensure the gradient points down the slope
    if gradient[2] > 0:
        return -1*gradient
    else:
        return gradient


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
                    grid_vector[i][j] = calculate_gradient(indicies, data, (x_start, y_start, x_finish, y_finish))

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


def print_grid(array_2d, formatting):
    #######################################
    #
    # Prints a 2D array as a grid
    #
    ######################################
    for row in array_2d:
        print_row = "";
        for val in row:
            print_row += formatting.format(val[Z])
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
    for i in range(GRID_SIZE_Y):
        magArr = []
        xRow = []
        yRow = []
        for j in range(GRID_SIZE_X):
            if (data[i][j][Z] == 0):
                magArr.append(0)
                xRow.append(0)
                yRow.append(0)
            else:
                magArr.append(abs(data[i][j][Z])*100)
                xRow.append(data[i][j][X])
                yRow.append(-1*data[i][j][Y]) # Y positive axis is downward, had to flip to get arrows in correct direction
        mag.append(magArr)
        xx.append(xRow)
        yy.append(yRow)

    # Normalize arrows for quiver plot
    #[qX, qY] = normalize(xx, yy)

    # Plot
    plt.quiver(xx, yy, scale=7, scale_units="inches", pivot="mid")
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
    ply_file = Path(output_folder, PLY_FILE_PATH)

    gradient_grid = create_gradient_grid(ply_file, store_gradients, read_gradients)

    plot_green(gradient_grid)

    return


# Insertion point
if __name__ == '__main__':
    # Read in arguments
    parser = argparse.ArgumentParser(description='Find slopes from a ply file')
    parser.add_argument('output_folder', metavar='file', type=str, default=Path('DataTest', 'PICS for GPS-20220412T022518Z-001', 'output'), help='Output folder path')
    parser.add_argument('--store_gradients', action='store_true', help='Store calculated gradients to memory')
    parser.add_argument('--read_gradients', action='store_true', help='Get gradients from memory')

    args = parser.parse_args()

    generate_slope_map(args.output_folder, args.store_gradients, args.read_gradients)
