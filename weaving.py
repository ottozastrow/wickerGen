import logging
import numpy as np

from utils import *
from util_classes import * 
from knot import *
from knot_types import Mappings, KnotType


"""
slot indexes (for case of two bundles)
[[1, 2, 5, 6],
 [3, 0, 7, 4]]
"""

def weave_straight(strands: list[Strand], start:Pos, end:Pos, start_angle, end_angle):
    logging.debug("started straight bundle from z=%.2f to z=%.2f", start.z, end.z)

    assert len(strands) > 0
    assert(end.z < start.z), end
    height = start.z-end.z

    rotation = end_angle - start_angle
    # movement height is adjusted such that after N "weaves" the starting position is achieved
    adjusted_weave_height = calc_adjusted_weave_height(height, Arena.weave_cycle_height)
    weave_cycles = round(height/adjusted_weave_height)
    cycles_list = [Mappings.mapping_closed for i in range(weave_cycles)]

    x0 = np.linspace(start.x, end.x, weave_cycles * Arena.divide_steps)
    y0 = np.linspace(start.y, end.y, weave_cycles * Arena.divide_steps)

    weave_strands(strands, height, adjusted_weave_height, cycles_list, start.z, 
                  is_knot=False, x0=x0, y0=y0, start_angle=start_angle, stop_angle=end_angle)
    assert len(strands) == 4, len(strands)
    

def weave_knot(knot):
    """
    function uses knot instance to move strands. output are new groups of strands at new positions
    every knot consists of 1 on more weaves (from its cycles_list)
    """
    
    logging.debug("started knot at z=%.2f with id %d", knot.input_positions[0].z, knot.id)
    cycles_list = knot.knottype
    strands1 = knot.input_bundles[0]
    strands2 = knot.input_bundles[1]
    
    
    if strands1 is None :
        strands1 = [Strand(i) for i in range(4)]
        logging.debug("WARNING: unconnected knot at %s", knot.centers[1])
    elif strands2 is None:
        strands2 = [Strand(i) for i in range(4)]
        logging.debug("WARNING: unconnected knot at %s", knot.centers[1])
    
    assert len(strands1) == 4
    assert len(strands2) == 4

    strands = strands1 + strands2
    
    for strand in strands2:
        strand.knot_slot = strand.slot + len(strands2)
    for strand in strands1:
        strand.knot_slot = strand.slot

    height = len(cycles_list) * Arena.weave_cycle_height
    weave_strands(strands, height, Arena.weave_cycle_height, cycles_list, knot.input_positions[0].z,
                  is_knot=True, knot=knot, bundle_centers=knot.centers)


    knot.output_bundles[0] = [strand for strand in strands if strand.knot_slot < 4]
    knot.output_bundles[1] = [strand for strand in strands if strand.knot_slot >= 4]

    logging.debug("finished knot")

def weave_strands(strands, height, adjusted_weave_height, cycles_list, z_offset,
                  bundle_centers=None, knot=None, is_knot=None, 
                  x0=None, y0=None, start_angle=None, stop_angle=None):
    

    weave_cycles = len(cycles_list)
    z = np.linspace(z_offset, z_offset - height, weave_cycles * Arena.divide_steps, endpoint=False)

    for strand in strands:
        strand.z += list(z)
    if not is_knot: 
        # create a startangle and stopangle for all weave cycles
        angles = np.linspace(start_angle, stop_angle, weave_cycles + 1)
    else:
        angles = np.ones(weave_cycles +1) * knot.angle # TODO test replace with knot.angle?
    for cycle in range(weave_cycles):
        for i in range(len(strands)):

            strand = strands[i]
            movement = cycles_list[cycle][strand.knot_slot]


            if strand.knot_slot == movement['target']: # if strand is stationary
                # x_start,y_start = get_relative_knot_position(strand.knot_slot)
                # x_relative = np.zeros(Arena.divide_steps) + x_start
                # y_relative = np.zeros(Arena.divide_steps) + y_start
                x_relative, y_relative = compute_vis_curve(movement['direction'], 
                                                           angles[cycle], angles[cycle+1], stationary=True)
            else:
                x_relative, y_relative = compute_vis_curve(movement['direction'], 
                                                           angles[cycle], angles[cycle+1], stationary=False)
            
            if is_knot:
                x_absolute = bundle_centers[movement['cent']].x
                y_absolute = bundle_centers[movement['cent']].y
            else: # is bundle
                current_step = cycle * Arena.divide_steps
                x_absolute = x0[current_step:current_step + Arena.divide_steps]
                y_absolute = y0[current_step:current_step + Arena.divide_steps]
                
            strand.x += list(x_relative + x_absolute)
            strand.y += list(y_relative + y_absolute)
            strand.knot_slot = movement['target']


    for strand in strands:
        strand.slot = strand.knot_slot % 4

    
