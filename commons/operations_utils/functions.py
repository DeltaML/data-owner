import numpy as np


def mean_square_error(y_pred, y):
    """ 1/m * \sum_{i=1..m} (y_pred_i - y_i)^2 """
    return np.mean((y - y_pred) ** 2)

def pred_diff(y_pred, y):
    """ 1/m * \sum_{i=1..m} (y_pred_i - y_i)^2 """
    return (y - y_pred).tolist()

def sum_collection(x, y):
    if len(x) != len(y):
        raise ValueError('Encrypted vectors must have the same size')
    return x + y
