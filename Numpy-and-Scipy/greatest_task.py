
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import random

SEED = 21
random.seed(SEED)
np.random.seed(SEED)

def find_largest_element(array, n=7):
    # apply inplace to avoid creating a new object
    array.sort()
    # take top-n largest elements
    return array[-n:]
