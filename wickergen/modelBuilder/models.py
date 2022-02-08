from collections import defaultdict

import numpy as np
from braidGenerator import *
from braidGenerator.graph import add_link
from braidGenerator.knot import Knot
from braidGenerator.util_classes import KnotType, Pos
from braidGenerator.utils import angle_from_circle_slot


def generate_circular_knots(
    num_knots: int,
    z_position: float,
    radius: float,
    knottype,
    num_strands: int,
    angle_offset: float,
) -> list[Knot]:

    knots = []
    angles = np.linspace(0, 2 * np.pi - 2 * np.pi / num_knots, num_knots)
    for el_id in range(num_knots):
        angles_current = angles + angle_from_circle_slot(num_knots, angle_offset)

        x = radius * np.cos(angles_current[el_id])
        y = radius * np.sin(angles_current[el_id])
        knot = Knot(knottype, Pos(x, y, z_position), num_strands)
        knots.append(knot)
    return knots


def generate_nice_sample_graph():
    f = 1.0  # slim factor
    # layer_radia = [0.9/f, 0.7/f , 0.53/f, 0.64/f, 0.55/f, 0.64/f]  # square
    layer_radia = [
        1.11 / f,
        0.78 / f,
        0.55 / f,
        0.5 / f,
        0.53 / f,
        0.56 / f,
        0.6,
        0.65,
        0.72,
        0.8,
    ]  # round
    layer_heights = [2.5, 1.8, 1, 0.0, -1, -1.8, -2.6, -3.2, -4, -4.8]

    num_elements = 5

    layers = [[] for i in range(len(layer_radia))]
    knots = []
    links = defaultdict(list), defaultdict(list)  # will return [] instead of key error

    layer_radius = layer_radia[0]
    start_knots_diagonal = generate_circular_knots(
        num_elements * 2,
        layer_heights[0],
        layer_radia[0],
        KnotType.startknot,
        4,
        angle_from_circle_slot(num_elements * 2, 0.5),
    )
    layers[0] = start_knots_diagonal

    start_knots_vertical = generate_circular_knots(
        num_elements * 2,
        layer_heights[0],
        layer_radia[0],
        KnotType.startknot,
        8,
        angle_from_circle_slot(num_elements * 2, 0.0),
    )

    center_knots = [Knot(KnotType.startknot, Pos(0, 0, h)) for h in layer_heights]
    startknots = start_knots_diagonal + start_knots_vertical + [center_knots[0]]
    knots += startknots
    knots += center_knots

    for l in range(1, len(layer_radia)):
        layer_radius = layer_radia[l]
        angles = np.linspace(0, 2 * np.pi - 2 * np.pi / num_elements, num_elements)
        for el_id in range(num_elements):
            angles_current = angles + angle_from_circle_slot(num_elements, l / 2)
            x = layer_radius * np.cos(angles_current[el_id])
            y = layer_radius * np.sin(angles_current[el_id])
            knottype = [KnotType.move2, KnotType.move4, KnotType.move1][el_id % 3]
            knottype = KnotType.move2
            knot = Knot(knottype, Pos(x, y, layer_heights[l]))
            knots.append(knot)
            layers[l].append(knot)

            if l == 1:
                parent1 = start_knots_diagonal[(el_id * 2) % (num_elements * 2)]
                parent2 = start_knots_diagonal[(el_id * 2 + 1) % (num_elements * 2)]
                parent3 = start_knots_vertical[(el_id * 2 + 1) % (num_elements * 2)]

            elif l == 2:
                parent1 = layers[l - 1][(el_id + 1) % (num_elements)]
                parent2 = layers[l - 1][(el_id) % (num_elements)]
                parent3 = start_knots_vertical[(el_id * 2 + 2) % (num_elements * 2)]

            else:  # >2
                parent1 = layers[l - 1][(el_id + 1) % (num_elements)]
                parent2 = layers[l - 1][(el_id) % (num_elements)]
                parent3 = layers[l - 2][(el_id + 1) % num_elements]

            # if l%2:
            #     add_link(links, center_knots[l-1], knot)
            # else:
            #     add_link(links, layers[l-1][el_id], center_knots[l])
            add_link(links, parent1, knot)
            add_link(links, parent2, knot)
            add_link(links, parent3, knot)

        # add_link(links, center_knots[l-1], center_knots[l])

    return links, startknots, knots


def generate_sample_graph():
    """dummy function for testing"""
    startknots = [
        Knot(KnotType.startknot, Pos(0.0 * 3, 0.1, 0.8)),
        Knot(KnotType.startknot, Pos(0.13 * 3, 0.05, 0.8)),
        Knot(KnotType.startknot, Pos(0.17 * 3, 0.05, 0.8)),
        Knot(KnotType.startknot, Pos(0.3 * 3, 0.1, 0.8)),
        Knot(KnotType.startknot, Pos(0.0 * 3, 0.0, 0.0)),
        Knot(KnotType.startknot, Pos(0.3 * 3, 0.0, 0.0)),
        Knot(KnotType.startknot, Pos(-0.13 * 3, 0.0, 0.4)),
        Knot(KnotType.startknot, Pos(1, 0.2, 0.8)),
        Knot(KnotType.startknot, Pos(0.15, 0.0, 0.8)),
    ]
    k1 = Knot(KnotType.move2, Pos(0.05 * 3, 0, 0.4))
    k2 = Knot(KnotType.move4, Pos(0.25 * 3, 0, 0.4))

    k3 = Knot(KnotType.move2, Pos(0.0 * 3, 0, -0.1))
    k4 = Knot(KnotType.move2, Pos(0.15 * 3, 0.0, -0.1))

    k5 = Knot(KnotType.move2, Pos(0.05 * 3, 0.4, -0.5))
    k6 = Knot(KnotType.move2, Pos(0.25 * 3, 0.4, -0.5))
    # k7 = Knot(KnotType.move2, Pos(0.9, 0.6, 0.4))
    # k8 = Knot(KnotType.move2, Pos(0.8, 0.4, 0.0))
    knots = startknots + [k1, k2, k3, k4, k5, k6]

    links = defaultdict(list), defaultdict(list)

    add_link(links, startknots[0], k1)
    add_link(links, startknots[1], k1)
    add_link(links, startknots[8], k1)
    add_link(links, startknots[2], k2)
    add_link(links, startknots[3], k2)
    add_link(links, k1, k4)
    add_link(links, k1, k3)
    add_link(links, k2, k4)
    add_link(links, startknots[6], k3)
    add_link(links, k3, k5)
    add_link(links, k4, k5)
    add_link(links, k1, k5)

    return links, startknots, knots


def generate_knot_graph(inputs: int = 2):
    top_knots = generate_circular_knots(inputs, 1.6, 0.3, KnotType.startknot, 4, 0)
    middle_knot_top = Knot(KnotType.startknot, Pos(0, 0, 1.6), 8)
    middle_knot = Knot(KnotType.move2, Pos(0, 0, 0.8))
    middle_knot_bottom = Knot(KnotType.move2, Pos(0, 0, 0.0))

    endknots = generate_circular_knots(inputs, 0, 0.3, KnotType.move2, 4, 0)

    endknots2 = generate_circular_knots(inputs, 0.8, 0.3, KnotType.move2, 4, 0)

    startknots = top_knots + [middle_knot_top]
    knots = startknots + [middle_knot, middle_knot_bottom] + endknots + endknots2
    links = defaultdict(list), defaultdict(list)  # will return [] instead of key error

    for i in range(inputs):
        add_link(links, top_knots[i], middle_knot)
        add_link(links, middle_knot, endknots[i])
        # add_link(links, top_knots[i], endknots2[i])
        # add_link(links, endknots2[i], endknots[i])
        # add_link(links, middle_knot_top, endknots2[i])
        # add_link(links, endknots2[i], middle_knot_bottom)
    add_link(links, middle_knot_top, middle_knot)
    add_link(links, middle_knot, middle_knot_bottom)

    return links, startknots, knots
