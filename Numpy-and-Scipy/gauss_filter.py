
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np

def gauss_filter(sigma = 1.0, mu = 0.0):
    x = np.linspace(-1, 1, 10, endpoint=True)
    y = np.linspace(-1, 1, 10, endpoint=True)
    xv, yv = np.meshgrid(x, y)

    nom = (np.sqrt(np.power(xv, 2) + np.power(yv, 2)) - mu) ** 2
    denom = 2 * (sigma ** 2)

    res = np.exp(- nom / denom)
    return res
