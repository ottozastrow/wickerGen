import numpy as np
from numpy import cos, divide, sin
import math

from util_classes import *


pi = np.pi


def rotate(origin: Pos, point: Pos, angle: float):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin.x, origin.y
    px, py = point.x, point.y

    point.x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    point.y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)


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

def circle_points(num_slots, angle_offset, radius):
    num_elements = num_slots
    angles = np.linspace(angle_offset + 0, angle_offset + 2*np.pi -2*np.pi/(num_elements), num_elements)
    x, y = [], []
    for el_id in range(num_elements):
        angles_current = angles + 2*np.pi / (num_elements) / 2
        y.append(radius * sin(angles_current[el_id]))
        x.append(radius * cos(angles_current[el_id]))
    return x, y


def generate_strands(num_slots):
    return [Strand(i) for i in range(num_slots)]

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

def calc_adjusted_weave_height(height, standard_cycle_height):
    num_cycles = height // standard_cycle_height
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


def points_list_from_strand_xyz(strand) -> list[list[float]]:
    """ creates and returns list of points from lists of x,y,z """
    histlen = len(strand.x)
    points = []
    for i in range(histlen):
        points.append([strand.x[i], strand.y[i], strand.z[i]])
    return points



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
