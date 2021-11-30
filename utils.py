from math import sin, cos, pi
from random import random

def uniform_direction():
    angle = random() * 2 * pi

    return cos(angle), sin(angle)