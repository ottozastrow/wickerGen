import numpy as np
from numpy import cos, sin

from util_classes import *


pi = np.pi


import math

def rotate(origin: Pos, point: Pos, angle: float):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin.x, origin.y
    px, py = point.x, point.y

    point.x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    point.y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    


def get_relative_knot_position(slot_knot):
    # 1,2,3,0
    slot = slot_knot % 4
    r = Arena.ellipse_b
    if slot==0:
        # topleft
        return r, -r
    elif slot==1: # topright
        return -r, r
    elif slot==2: # bottomleft
        return r, r
    else: # bottomright slot==3
        return -r, -r


def compute_vis_curve(direction, start_angle, stop_angle, stationary=False):
    
    directions = {
        'upleft': {'offset': 0, 'rotation': pi/2*3 + pi/4},
        'downright':    {'offset': 1, 'rotation': pi/2*3 + pi/4},
        'downleft':  {'offset': 0, 'rotation': pi/4},
        'upright':   {'offset': 1, 'rotation': pi/4},
    }
    offset = directions[direction]['offset']
    rotation = directions[direction]['rotation']
    bundle_twist = np.linspace(start_angle, stop_angle, Arena.divide_steps)
    if stationary:
        t = np.zeros(Arena.divide_steps) + offset * np.pi
    else:
        t = np.linspace(0, np.pi - np.pi/Arena.divide_steps, Arena.divide_steps) + offset * np.pi
    x = Arena.ellipse_a*cos(t)*cos(rotation + bundle_twist) - Arena.ellipse_b * sin(t) * sin(rotation + bundle_twist)
    y = Arena.ellipse_b*sin(t)*cos(rotation + bundle_twist) + Arena.ellipse_a * cos(t) * sin(rotation + bundle_twist)
    
    return x,y

def calc_adjusted_weave_height(height, standard_cycle_height):
    num_cycles = height // standard_cycle_height
    adjusted_weave_height = height / num_cycles

    return adjusted_weave_height
