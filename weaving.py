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
    cycles_list = []

    # weaving consist of two moves.
    for i in range(weave_cycles):
        cycles_list += [Mappings.mapping_straight, Mappings.mapping_straight_reversed]


    # absolute positions for bundles defined by interpolating between start and stop
    x0 = np.linspace(start.x, end.x, 2 * weave_cycles * Arena.divide_steps)
    y0 = np.linspace(start.y, end.y, 2 * weave_cycles * Arena.divide_steps)

    weave_strands(strands, height, adjusted_weave_height, cycles_list, start.z, 
                  is_knot=False, x0=x0, y0=y0, start_angle=start_angle, stop_angle=end_angle)
    assert len(strands) == 4, len(strands)



def weave_straight_new(strands: list[Strand], start:Pos, end:Pos, start_angle, end_angle):
    logging.debug("started straight bundle from z=%.2f to z=%.2f", start.z, end.z)

    assert len(strands) > 0
    assert(end.z < start.z), end
    height = start.z-end.z

    # movement height is adjusted such that after N "weaves" the starting position is achieved
    adjusted_weave_height = calc_adjusted_weave_height(height, Arena.weave_cycle_height)
    weave_cycles = round(height/adjusted_weave_height)

    divide_steps = 2
    # absolute positions for bundles defined by interpolating between start and stop
    x0 = np.linspace(start.x, end.x, weave_cycles * divide_steps)
    y0 = np.linspace(start.y, end.y, weave_cycles * divide_steps)


    z = np.linspace(start.z, start.z - height, weave_cycles * divide_steps, endpoint=False)

    for strand in strands:
        strand.z += list(z)
    
    angles = np.linspace(start_angle, end_angle, weave_cycles + 1)
    for cycle in range(weave_cycles):
        
        for i in range(len(strands)):
        # for i in strand_indices:
            strand = strands[i]
            x_relative, y_relative = calc_relative_strand_movement(strand, i,
                                                                   cycle%2,  # every second cycle is reversed
                                                                   angles[cycle], angles[cycle+1])
           
            current_step = cycle * divide_steps
            x_absolute = x0[current_step:current_step + divide_steps]
            y_absolute = y0[current_step:current_step + divide_steps]
                
            strand.x += list(x_relative + x_absolute)
            strand.y += list(y_relative + y_absolute)


def calc_relative_strand_movement(strand, i, is_reversed, start_angle, stop_angle):
    num_slots = 4
    circle_points(num_slots, 0, 0)
    x, y = [], []

    x_center,y_center = circle_points(num_slots, start_angle, Arena.straight_braid_radius)
    offset_angle = np.pi * 2 / num_slots / 2  # move half a slot forward
    if i%2:
        offset_angle *= -1
    x_inner,y_inner = circle_points(num_slots, start_angle + offset_angle, Arena.straight_braid_radius * 0.6)
    x_outer,y_outer = circle_points(num_slots, start_angle + offset_angle, Arena.straight_braid_radius)

    slot = strand.slot

    if slot % 2:
        x.append(x_inner[(slot)%num_slots])
        y.append(y_inner[(slot)%num_slots])

        x.append(x_center[(slot)%num_slots])
        y.append(y_center[(slot)%num_slots])
    else:
        x.append(x_outer[(slot)%num_slots])
        y.append(y_outer[(slot)%num_slots])

        x.append(x_center[(slot)%num_slots])
        y.append(y_center[(slot)%num_slots])

    if i % 2:
         strand.slot = (strand.slot + 1) % num_slots
    else:
         strand.slot = (strand.slot -1) % num_slots

    return x,y


def weave_knot_old(knot):
    """
    function uses knot instance to move strands. output are new groups of strands at new positions
    every knot consists of 1 on more weaves (from its cycles_list)
    """
    
    logging.debug("started knot at z=%.2f with id %d", knot.input_positions[0].z, knot.id)
    cycles_list = knot.knottype
    strands1 = knot.input_bundles[0]
    strands2 = knot.input_bundles[1]
    
    if strands1 is None :
        strands1 = generate_strands(4)
        logging.debug("WARNING: unconnected knot at %s", knot.pos)
    elif strands2 is None:
        strands2 = generate_strands(4)
        logging.debug("WARNING: unconnected knot at %s", knot.pos)
    
    assert len(strands1) == 4
    assert len(strands2) == 4

    strands = strands1 + strands2
    
    for strand in strands2:
        strand.knot_slot = strand.slot + len(strands2)
    for strand in strands1:
        strand.knot_slot = strand.slot

    height = len(cycles_list) * Arena.knot_cycle_height
    weave_strands(strands, height, Arena.knot_cycle_height, cycles_list, knot.input_positions[0].z,
                  is_knot=True, knot=knot, bundle_centers=knot.centers)

    knot.output_bundles[0] = [strand for strand in strands if strand.knot_slot < 4]
    knot.output_bundles[1] = [strand for strand in strands if strand.knot_slot >= 4]

    logging.debug("finished knot")

def weave_knot(knot):
    """
    function uses knot instance to move strands. output are new groups of strands at new positions
    every knot consists of 1 on more weaves (from its cycles_list)
    """
    
    logging.debug("started knot at z=%.2f with id %d", knot.input_positions[0].z, knot.id)
    cycles_list = knot.knottype
    ibs = knot.input_bundles
    strands = []
    for ib in ibs:
        if ib is None:
            ib = generate_strands(4) 
            logging.debug("WARNING: unconnected knot")
        strands += ib

    bundle_radius = Arena.strand_width * max([len(bundle) for bundle in ibs])

    # first: align points in a neet row (per bundle), such that bundles are parallel to each other
    for i in range(len(ibs)):
        i_start = -len(ibs) // 2
        for j in range(len(ibs[i])):
            j_start = -len(ibs[i]) // 2
            x = knot.pos.x + bundle_radius * (j + j_start)
            y = knot.pos.y + bundle_radius * (i + i_start)
            z = knot.pos.z + Arena.knot_cycle_height / 4
            tmp_pos = Pos(x,y,z)
            rotate(knot.pos, tmp_pos, knot.angle - np.pi / 2)
    
            ibs[i][j].x.append(tmp_pos.x)
            ibs[i][j].y.append(tmp_pos.y)
            ibs[i][j].z.append(tmp_pos.z)

    
    # exchange half of all strands between neighbouring bundles
    for i in range(len(ibs)-1):
        for j in range(min(len(ibs[i+1]), len(ibs[i])-1)):
            switch_over = (j+1)%2 # only switch every second strand
            if switch_over:
                # switching is done in a triangle. 
                
                strand_a = ibs[i][j]
                strand_b = ibs[i+1][j+1]
                strand_c = ibs[i][j+1]

                tmpx, tmpy, tmpz = strand_c.x[-1], strand_c.y[-1], strand_c.z[-1] - Arena.knot_cycle_height / 2
                tmpslot = strand_c.slot

                strand_c.x.append(strand_b.x[-1])
                strand_c.y.append(strand_b.y[-1])
                strand_c.z.append(strand_b.z[-1] - Arena.knot_cycle_height / 2)
                strand_c.slot = strand_b.slot

                strand_b.x.append(strand_a.x[-1])
                strand_b.y.append(strand_a.y[-1])
                strand_b.z.append(strand_a.z[-1] - Arena.knot_cycle_height / 2)
                strand_b.slot = strand_a.slot

                strand_a.x.append(tmpx)
                strand_a.y.append(tmpy)
                strand_a.z.append(tmpz)
                strand_a.slot = tmpslot
                
                ibs[i][j] = strand_b
                ibs[i+1][j+1] = strand_c
                ibs[i][j+1] = strand_a


    # set ouput bundles
    for i in range(len(ibs)):
        knot.output_bundles[i] = ibs[i]

    logging.debug("finished knot")


def weave_strands(strands, height, adjusted_weave_height, cycles_list, z_offset,
                  bundle_centers=None, knot=None, is_knot=None, 
                  x0=None, y0=None, start_angle=None, stop_angle=None):
    
  
    divide_steps = Arena.divide_knot_steps if is_knot else Arena.divide_steps

    weave_cycles = len(cycles_list)
    z = np.linspace(z_offset, z_offset - height, weave_cycles * divide_steps, endpoint=False)

    for strand in strands:
        strand.z += list(z)
    if not is_knot: 
        # create a startangle and stopangle for all weave cycles
        angles = np.linspace(start_angle, stop_angle, weave_cycles + 1)
    else:
        angles = np.ones(weave_cycles +1) * knot.angle
    for cycle in range(weave_cycles):
        for i in range(len(strands)):

            strand = strands[i]
            movement = cycles_list[cycle][strand.knot_slot]


            if strand.knot_slot == movement['target']: # if strand is stationary
                x_relative, y_relative = compute_vis_curve(movement['direction'], 
                                                           angles[cycle], angles[cycle+1], is_knot, stationary=True)
            else:
                x_relative, y_relative = compute_vis_curve(movement['direction'], 
                                                           angles[cycle], angles[cycle+1], is_knot, stationary=False)
            
            if is_knot:
                x_absolute = bundle_centers[movement['cent']].x
                y_absolute = bundle_centers[movement['cent']].y
            else: # is bundle
                current_step = cycle * divide_steps
                x_absolute = x0[current_step:current_step + divide_steps]
                y_absolute = y0[current_step:current_step + divide_steps]
                
            strand.x += list(x_relative + x_absolute)
            strand.y += list(y_relative + y_absolute)
            strand.knot_slot = movement['target']


    for strand in strands:
        strand.slot = strand.knot_slot % 4

    
