import numpy as np
from numpy import cos, divide, sin

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


def min_max_z_from_strands(strands):
    """ returns the maximum and minimum z value (time) of a list of strands"""
    minz = None
    maxz = 0
    for strand in strands:
        if len(strand.z) > 0:
            if strand.z[-1] > maxz:
                maxz = strand.z[-1]
            if minz is None or strand.z[0] < minz:
                minz = strand.z[0]
    if minz is None:
        minz = 0
    return minz, maxz


def compute_vis_curve(direction, start_angle, stop_angle, is_knot, stationary=False):
    if is_knot:
        divide_steps = Arena.divide_knot_steps
    else:
        divide_steps = Arena.divide_steps
    
    directions = {
        'upleft': {'offset': 0, 'rotation': pi/2*3 + pi/4},
        'downright':    {'offset': 1, 'rotation': pi/2*3 + pi/4},
        'downleft':  {'offset': 0, 'rotation': pi/4},
        'upright':   {'offset': 1, 'rotation': pi/4},
    }
    offset = directions[direction]['offset']
    rotation = directions[direction]['rotation']
    bundle_twist = np.linspace(start_angle, stop_angle, divide_steps)
    if stationary:
        t = np.zeros(divide_steps) + offset * np.pi
    else:
        t = np.linspace(0, np.pi - np.pi/divide_steps, divide_steps) + offset * np.pi
    x = Arena.ellipse_a*cos(t)*cos(rotation + bundle_twist) - Arena.ellipse_b * sin(t) * sin(rotation + bundle_twist)
    y = Arena.ellipse_b*sin(t)*cos(rotation + bundle_twist) + Arena.ellipse_a * cos(t) * sin(rotation + bundle_twist)
    
    return x,y

def calc_adjusted_double_weave_height(height, standard_cycle_height):

    num_cycles = height // (standard_cycle_height)
    adjusted_weave_height = height / num_cycles

    return adjusted_weave_height


def round_step_size(quantities, step_size) -> float:
    """Rounds a given quantity to a specific step size
    :param quantity: required
    :param step_size: required
    :return: decimal
    """
    precision: int = int(round(-math.log(step_size, 10), 0))
    return float(round(quantities, precision))

def interpolate_strands(strands, divide_steps):
    for strand in strands:
        if len(strand.x)>0:
            x = np.array(strand.x)
            y = np.array(strand.y)
            z = np.array(strand.z)
            
            minz = round_step_size(min(z), 0.01)
            maxz = round_step_size(max(z), 0.01)

            fx = interpolate.interp1d(z, x, kind="cubic", fill_value="extrapolate")
            fy = interpolate.interp1d(z, y, kind='cubic', fill_value="extrapolate")
            newz = np.linspace(minz, maxz, len(z)*divide_steps)
            xnew = fx(newz)   # use interpolation function returned by `interp1d`
            ynew = fy(newz)   # use interpolation function returned by `interp1d`
            strand.x = list(xnew)
            strand.y = list(ynew)
            strand.z = list(newz)


def compute_robobt_position(strand, index=2):
    if len(strand.x)>2:
        # get arrays of last 2 points for interpolation. minimum 2 are required for linear interpolation
        x = np.array(strand.x)[index-2:index]
        y = np.array(strand.y)[index-2:index]
        z = np.array(strand.z)[index-2:index]
        minz = round_step_size(min(z), 0.001)
        maxz = round_step_size(max(z), 0.001)


        fx = interpolate.interp1d(z, x, kind="linear", fill_value="extrapolate")
        fy = interpolate.interp1d(z, y, kind='linear', fill_value="extrapolate")
        floor_z = minz-0.15
        newz = np.linspace(floor_z, maxz, 2)
        xnew = fx(newz)   # use interpolation function returned by `interp1d`
        ynew = fy(newz)   # use interpolation function returned by `interp1d`
        
        # -1 added for better visualization
        return xnew[0], ynew[0], floor_z
    else:
        assert False
