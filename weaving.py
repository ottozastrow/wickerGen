import logging
import numpy as np

from utils import *
from util_classes import * 
from knot import *
import math


def weave_straight_new(strands: list[Strand], start:Pos, end:Pos, start_angle, end_angle, weave_cycles=None):
    logging.debug("started straight bundle from z=%.2f to z=%.2f", start.z, end.z)

    assert len(strands) > 0
    assert(end.z < start.z), end
    height = start.z-end.z
    num_strands = len(strands)

    # movement height is adjusted such that after N "weaves" the starting position is achieved
    if weave_cycles == None:
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
            x_relative, y_relative = calc_relative_strand_movement(strand, i, num_strands,angles[cycle])
           
            current_step = cycle * divide_steps
            x_absolute = x0[current_step:current_step + divide_steps]
            y_absolute = y0[current_step:current_step + divide_steps]
                
            strand.x += list(x_relative + x_absolute)
            strand.y += list(y_relative + y_absolute)


def calc_relative_strand_movement(strand, i, num_slots, start_angle):
    circle_points(num_slots, 0, 0)
    x, y = [], []
    braid_radius = 2 * Arena.strand_width * math.sqrt(num_slots)

    x_center,y_center = circle_points(num_slots, start_angle, braid_radius )
    offset_angle = np.pi * 2 / num_slots / 2  # move half a slot forward
    if i%2:
        offset_angle *= -1
    x_inner,y_inner = circle_points(num_slots, start_angle + offset_angle, braid_radius * 0.6)
    x_outer,y_outer = circle_points(num_slots, start_angle + offset_angle, braid_radius)

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


def weave_knot(knot):
    ibs = knot.input_bundles
    strands = []
    current_strand_count = 0
    bundle_sizes = []
    for ib in ibs:
        if ib is None:
            ib = generate_strands(4) 
            logging.debug("WARNING: unconnected knot")
        current_strand_count += len(ib)
        for strand in strands:
            strand.slot += len(ib)
        strands += ib
        bundle_sizes.append(len(ib))

    start =  knot.input_positions[1]
    start.z -= knot.height / 5
    end = knot.output_positions[1]
    end.z += knot.height / 5
    angle = -np.pi / 2
    weave_straight_new(strands, start, end, knot.angle + angle, knot.angle + angle, weave_cycles=2)

    # set ouput bundles
    counter = 0
    for i in range(len(bundle_sizes)):
        current_strands = []
        for j in range(bundle_sizes[i]):                
            current_strand = strands[counter]
            strand.slot = j
            current_strands.append(current_strand)
            counter += 1
        knot.output_bundles[i] = current_strands

    

def weave_knot_triangle(knot):
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

    # dynamic bundle radius
    #bundle_radius = Arena.strand_width * max([len(bundle) for bundle in ibs])

    # first: align points in a neet row (per bundle), such that bundles are parallel to each other
    for i in range(len(ibs)):
        i_start = -len(ibs) // 2
        for j in range(len(ibs[i])):
            j_start = -len(ibs[i]) // 2
            x = knot.pos.x + Arena.knot_gridsize_x * (j + j_start)
            y = knot.pos.y + Arena.knot_gridsize_y * (i + i_start)
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

                tmpx, tmpy = strand_c.x[-1], strand_c.y[-1]
                tmpslot = strand_c.slot

                strand_c.x.append(strand_b.x[-1])
                strand_c.y.append(strand_b.y[-1])
                strand_c.z.append(strand_c.z[-1] - Arena.knot_cycle_height)
                strand_c.slot = strand_b.slot

                strand_b.x.append(strand_a.x[-1])
                strand_b.y.append(strand_a.y[-1])
                strand_b.z.append(strand_b.z[-1] - Arena.knot_cycle_height)
                strand_b.slot = strand_a.slot

                strand_a.x.append(tmpx)
                strand_a.y.append(tmpy)
                strand_a.z.append(strand_a.z[-1] - Arena.knot_cycle_height)
                strand_a.slot = tmpslot
                
                ibs[i][j] = strand_b
                ibs[i+1][j+1] = strand_c
                ibs[i][j+1] = strand_a


    # set ouput bundles
    for i in range(len(ibs)):
        knot.output_bundles[i] = ibs[i]

    logging.debug("finished knot")


