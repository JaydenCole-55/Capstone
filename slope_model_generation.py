###################################################################################################
#
#                                  SLOPE MODEL GENERATION MODULE
#
#
# Generates a 2D slope map from a polygon mesh
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
import numpy as np
import copy
from pathlib import Path

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
    def __init__(self, num_verticies, num_faces):

        # Allocate memory for vertex data
        self.x       = np.zeros(num_verticies)
        self.y       = np.zeros(num_verticies)
        self.z       = np.zeros(num_verticies)
        self.red     = np.zeros(num_verticies)
        self.green   = np.zeros(num_verticies)
        self.blue    = np.zeros(num_verticies)
        self.alpha   = np.zeros(num_verticies)
        self.quality = np.zeros(num_verticies)

        # Allocate memory for faces data
        lst1 = np.zeros(num_faces)
        lst2 = np.zeros(num_faces)
        lst3 = np.zeros(num_faces)
        
        self.faces = list(zip(lst1, lst2, lst3))


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
    j = 0

    with open(ply_file) as plyFile:
        # Iterate through each line of the file storing the data
        for line in plyFile:

            # Parse information from file header
            if in_file_header:
                if 'end_header' in line:
                    in_file_header = False
                    s_data = Surface_Data(num_verticies, num_faces)

                elif 'element' in line and 'vertex' in line:
                    num_verticies = int(line.split()[2])

                elif 'element' in line and 'face' in line:
                    num_faces = int(line.split()[2])

                continue
            else:
                # Store vertex data to memory
                if i < num_verticies:
                    x, y, z, _, _, _, _, _ = line.split()

                    s_data.x[i] = x
                    s_data.y[i] = y
                    s_data.z[i] = z

                    i+=1
                # Store face data to memory
                else:
                    _, v1, v2, v3 = line.split()

                    s_data.faces[j] = (int(v1), int(v2), int(v3))

                    j+=1

    print('Finished reading file\n')
    return s_data


def calculate_slope(indicies, s_data, grid_location):
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
        # TODO: sometimes there are multiples of the same point in the code,
        # for now, return a null gradient - Preferably ply file creation would check for no double
        # points
        print("Cannot compute a gradient in a grid section due to multiples of the same point")

        return (0, 0, 0)

    # print("Solution:")
    # print("%f x + %f y + %f = z" % (fit[0], fit[1], fit[2]))

    # Find x, y pt of maximum height within this grid area (will be on a corner)
    left_bottom  = [x_min, y_min, float(np.squeeze(np.array(x_min * fit[0] + y_min * fit[1] + fit[2])))]
    left_top     = [x_min, y_max, float(np.squeeze(np.array(x_min * fit[0] + y_max * fit[1] + fit[2])))]
    right_bottom = [x_max, y_min, float(np.squeeze(np.array(x_max * fit[0] + y_min * fit[1] + fit[2])))]
    right_top    = [x_max, y_max, float(np.squeeze(np.array(x_max * fit[0] + y_max * fit[1] + fit[2])))]

    # Determine the gradient from the relative z heights of the 4 corners on the plane
    if abs(left_top[2] - right_bottom[2]) > abs(left_bottom[2] - right_top[2]):
        gradient = np.subtract(left_top, right_bottom)
    elif abs(left_bottom[2] - right_top[2]) > abs(left_top[2] - right_bottom[2]):
        gradient = np.subtract(left_bottom, right_top)
    elif left_top[2] - right_top[2] == 0:
        gradient = np.subtract(left_top, left_bottom)
    elif left_top[2] - left_bottom[2] == 0:
        gradient = np.subtract(left_top, right_top)

    # Ensure the gradient points down the slope
    if gradient[2] > 0:
        return -1*gradient
    else:
        return gradient


# Insertion point
if __name__ == '__main__':
    # Display output
    print()
    print('#'*75 + '\n')
    print('Starting slope generation module...\n')
    print('#'*75 + '\n')

    # Test the modules functions from this insertion point
    data_location = Path('Data/2022-02-26_GrassPatch01/Hole01/Images')

    ply_file = data_location / 'mesh1.1.ply'
    grid_size_x = 20
    grid_size_y = 20

    # Allocate grid vector memory
    lst = np.zeros(grid_size_x)
    intermediate_step = list(zip(lst, lst, lst))
    grid_vector = []
    for i in range(grid_size_y):
        grid_vector.append(copy.deepcopy(intermediate_step)) 
    
    # Read in data
    data = read_ply_file(ply_file)

    # Now that the data is collected, create a 20x20 grid from min & max x and y points
    max_x = max(data.x)
    min_x = min(data.x)
    max_y = max(data.y)
    min_y = min(data.y)

    # Determine grid boxes dimensions
    length_x = max_x - min_x
    step_x = length_x/grid_size_x

    length_y = max_y - min_y
    step_y = length_y/grid_size_y

    # Go through each grid area and find average slope
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            # Determine grid area x and y selections
            x_start  = min_x + step_x*i
            x_finish = min_x + step_x*(i+1)
            y_start  = min_y + step_y*j
            y_finish = min_y + step_y*(j+1)

            # Find all points within this grid area
            indicies = list(filter(lambda k: data.x[k] >= x_start and data.x[k] <= x_finish and data.y[k] >= y_start and data.y[k] <= y_finish, range(len(data.x))))

            if len(indicies) <= 1:
                # No gradient can be given for a grid area that contains less than two points
                continue
            else:
                # Find a vector that averages the slopes of the grid area points
                grid_vector[i][j] = calculate_slope(indicies, data, (x_start, y_start, x_finish, y_finish))
                pass

    print('Done')
