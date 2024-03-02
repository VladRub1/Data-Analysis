
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import random
from scipy.signal import convolve2d

SEED=21
random.seed(SEED)
np.random.seed(SEED)

def game_of_life_next_step(array):
    """
    Function documentation from scipy:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve2d.html
    """
    # Idea: walk across the game field with a convolution kernel symbolizing a pattern of possible neighbors
    # then the result will be the number of neighbors
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    # mode='same' -- to make the output the same size as the array
    # boundary='wrap' -- symbolizes the looping of the field
    neighbors_counts = convolve2d(array, kernel, mode='same', boundary='wrap')

    # end-of-life conditions
    array[(array == 1) & (neighbors_counts < 2)] = 0
    array[(array == 1) & (neighbors_counts > 3)] = 0
    # conditions for the emergence of life
    array[(array == 0) & (neighbors_counts == 3)] = 1

    # the cells on the border must die
    # 1-st row
    array[0, :] = 0
    # 1-st col
    array[:, 0] = 0
    # last row
    array[-1, :] = 0
    # last col
    array[:, -1] = 0

    return array
