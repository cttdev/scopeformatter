from enum import Enum

import numpy as np

class InterpolationTypes(Enum):
    Linear = 1
    Quadratic = 2
    Cubic = 3
    Exponential = 4

class DraculaColors(Enum):
    background = "#282a36"
    current_line = "#44475a"
    foreground = "#f8f8f2"
    comment = "#6272a4"

class DraculaAccents(Enum):
    cyan = "#8be9fd"
    green = "#50fa7b"
    orange = "#ffb86c"
    pink = "#ff79c6"
    purple = "#bd93f9"
    red = "#ff5555"
    yellow = "#f1fa8c"


def polynomial_equation_generator(model):
    degree = len(model) - 1
    polynomial = ""

    for i in range(degree):
        if not degree == 1:
            polynomial += str(abs(model[i])) + " x^" + str(degree) + (" + " if model[i+1] > 0 else " - ")
        else :
            polynomial += str(abs(model[i])) + " x" + (" + " if model[i+1] > 0 else " - ")
        degree -=1
    polynomial += str(abs(model[-1]))

    return polynomial

def exponential_equation_generator(linearized_model):
    return str(np.exp(linearized_model[1])) + " * e^" + str(linearized_model[0]) + " * x"