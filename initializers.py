from math import sqrt, sin, cos, pi
from random import random, uniform

from utils import uniform_direction

def center(config_dict):
    for _ in range(config_dict["n_agents"]):
        # position
        yield config_dict["width"] / 2
        yield config_dict["height"] / 2

        # direction
        dx, dy = uniform_direction()

        yield dx
        yield dy


def disk(config_dict):
    for _ in range(config_dict["n_agents"]):
        # position: uniformly within a centered disk of radius R
        R = 500

        r = R * sqrt(random())
        theta = random() * 2 * pi

        x =  config_dict["width"] / 2 + r * cos(theta)
        y =  config_dict["height"] / 2 + r * sin(theta)

        yield x
        yield y

        # direction: facing towards the center
        dx = config_dict["width"] / 2 - x
        dy = config_dict["height"] / 2 - y
        length = sqrt(dx ** 2 + dy ** 2)

        yield dx / length
        yield dy / length


def random_uniform(config_dict):
    for _ in range(config_dict["n_agents"]):
        yield random() * config_dict["width"]
        yield random() * config_dict["height"]

        dx, dy = uniform_direction()

        yield dx
        yield dy