import math

import numpy as np
from numpy import cos, sin
from scipy import interpolate

from .util_classes import Arena, Pos, Strand

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
    """returns the maximum and minimum z value (time) of a list of strands"""
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
    angles = np.linspace(
        angle_offset + 0,
        angle_offset + 2 * np.pi - 2 * np.pi / (num_elements),
        num_elements,
    )
    x, y = [], []
    for el_id in range(num_elements):
        angles_current = angles + 2 * np.pi / (num_elements) / 2
        y.append(radius * sin(angles_current[el_id]))
        x.append(radius * cos(angles_current[el_id]))
    return x, y


def generate_strands(num_slots: int) -> list[Strand]:
    return [Strand(i) for i in range(num_slots)]


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
    """creates and returns list of points from lists of x,y,z"""
    histlen = len(strand.x)
    points = []
    for i in range(histlen):
        points.append([strand.x[i], strand.y[i], strand.z[i]])
    return points


def angle_from_circle_slot(total_slots, target_slot) -> float:
    """helper to compute angle offsets for elements arranged in a circle"""
    return 2 * np.pi / total_slots * target_slot


def generate_circular_positions(
    center: Pos,
    num_positions: int,
    z_position: float,
    radius: float,
    angle_offset: float,
) -> list[Pos]:
    positions = []
    angles = np.linspace(0, 2 * np.pi - 2 * np.pi / num_positions, num_positions)
    for el_id in range(num_positions):
        angles_current = angles + angle_from_circle_slot(num_positions, angle_offset)

        x = radius * cos(angles_current[el_id])
        y = radius * sin(angles_current[el_id])
        knot = Pos(x + center.x, y + center.y, z_position)
        positions.append(knot)
    return positions


def interpolate_strands(strands, kind="cubic", step_size=0.01):
    minz, maxz = None, None

    # first get global max and minimum z value, in order to create global grid
    for strand in strands:
        if len(strand.z) > 0:
            z = np.array(strand.z)
            currentmin = round_step_size(min(z), step_size)
            currentmax = round_step_size(max(z), step_size)
            if minz == None or currentmin < minz:
                minz = currentmin
            if maxz == None or currentmax > maxz:
                maxz = currentmax
    num_steps = (
        maxz - minz
    ) / Arena.interpolate_steps_per_meter  # 0.005 is steps per meter

    global_z = np.linspace(minz, maxz, int(num_steps))  # global grid

    # interpolate along this grid (in the z interval in which the strand is defined)
    for strand in strands:
        if len(strand.z) > 0:
            x = np.array(strand.x)
            y = np.array(strand.y)
            z = np.array(strand.z)

            minz = round_step_size(min(z), step_size)
            maxz = round_step_size(max(z), step_size)

            fx = interpolate.interp1d(z, x, kind=kind, fill_value="extrapolate")
            fy = interpolate.interp1d(z, y, kind=kind, fill_value="extrapolate")

            currentz = [zi for zi in global_z if minz < zi and zi < maxz]

            xnew = fx(currentz)  # use interpolation function returned by `interp1d`
            ynew = fy(currentz)  # use interpolation function returned by `interp1d`
            strand.x = list(xnew)
            strand.y = list(ynew)
            strand.z = list(currentz)


def compute_robobt_position(strand: Strand, index=2) -> tuple[float, float, float]:
    if len(strand.x) > 2:
        # get arrays of last 2 points for interpolation. minimum 2 are required for linear interpolation
        x = np.array(strand.x)[index - 2 : index]
        y = np.array(strand.y)[index - 2 : index]
        z = np.array(strand.z)[index - 2 : index]
        minz = round_step_size(min(z), 0.001)
        maxz = round_step_size(max(z), 0.001)

        fx = interpolate.interp1d(z, x, kind="linear", fill_value="extrapolate")
        fy = interpolate.interp1d(z, y, kind="linear", fill_value="extrapolate")
        floor_z = minz - 0.15
        newz = np.linspace(floor_z, maxz, 2)
        xnew = fx(newz)  # use interpolation function returned by `interp1d`
        ynew = fy(newz)  # use interpolation function returned by `interp1d`

        # -1 added for better visualization
        return xnew[0], ynew[0], floor_z
    else:
        assert False
