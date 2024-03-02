
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import random

SEED = 21
random.seed(SEED)
np.random.seed(SEED)

def task_00(A):
    res = np.einsum('i->', A)
    return res

def task_01(A, B):
    res = np.einsum('i,i->i', A, B)
    return res

def task_02(A, B):
    res = np.einsum('i,i->', A, B)
    return res

def task_03(A, B):
    res = np.einsum('i,j->ij', A, B)
    return res
