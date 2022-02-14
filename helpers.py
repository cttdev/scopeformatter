from enum import Enum

class InterpolationTypes(Enum):
    Linear = 1
    Quadratic = 2
    Cubic = 3

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
