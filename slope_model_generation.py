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
#   3. Calculate slopes within grid
#   4. Output graphical interpretation of the slopes on the green
#
###################################################################################################
from pathlib import Path
import numpy as np

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
                    x, y, z, r, g, b, a, q = line.split()

                    s_data.x[i] = x
                    s_data.y[i] = y
                    s_data.z[i] = z
                    # s_data.red[i] = r
                    # s_data.green[i] = g
                    # s_data.blue[i] = b
                    # s_data.alpha[i] = a
                    # s_data.quality[i] = q
                    i+=1
                # Store face data to memory
                else:
                    _, v1, v2, v3 = line.split()

                    s_data.faces[j] = (int(v1), int(v2), int(v3))

                    j+=1

    print('Finished reading file')
    return s_data


def calculate_slope(indicies, s_data):
    #######################################
    #
    # Calculates the slope of the given indicies from the most top left corner point
    #
    # Input: list of indicies (ints), the vertex data object
    # Returns: Vector sum (tuple as (x, y, z))
    #
    ######################################

    # 1. Find upper left point of the indicies indicated within the vertex data object
    # 2. Calculate the vectors between that point and all other indicies points
    # 3. Average the vectors
    # 4. Recursively call this function removing the top left point
    # 5. Sum the recursive call (4) and the averaged vector sum from (3)
    pass


# Insertion point
if __name__ == '__main__':
    # Test the modules functions from this insertion point
    data_location = Path('Data/2022-02-26_GrassPatch01/Hole01/Images')

    ply_file = data_location / 'mesh1.1.ply'
    grid_size_x = 20
    grid_size_y = 20

    # Allocate grid vector memory
    lst = np.zeros(grid_size_x)
    grid_vector = [list(zip(lst, lst, lst))] * grid_size_y
    
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

            if len(indicies) == 0:
                # No points found in this grid area, continue
                continue
            elif len(indicies) == 1:
                # No slope can be given for a grid area that contains one point
                continue
            elif len(indicies) >= 2:
                # Find a vector that averages the slopes of the grid area points
                grid_vector[i][j] = calculate_slope(indicies, data)

    print('Done')
