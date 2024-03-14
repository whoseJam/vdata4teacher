import numpy as np

def any2array(any):
    if type(any) == dict:
        return any.values()
    return any

def satisfy(any, cond):
    array, passed = any2array(any), 0
    for i in range(len(array)):
        if cond(array[i]):
            passed = passed + 1
    return 1.0 * passed / len(array)

def average(any):
    return np.average(any2array(any))

def passRate(any, limit):
    return satisfy(any, lambda x: x >= limit)

def max(any):
    return np.max(any2array(any))

def min(any):
    return np.min(any2array(any))

def std(any):
    return np.std(any2array(any))