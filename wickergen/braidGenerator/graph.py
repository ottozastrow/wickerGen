import logging

import numpy as np

from . import utils, weaving
from .knot import Knot
from .util_classes import KnotType


def choose_parent_child_link(parent: Knot, child: Knot):
    # decide which of the childrens inputs to connect to
    # by choosing the input output position combination with
    # the smalles euclid distance
    smallest_dist = None
    selected_inpos = None
    selected_outpos = None
    selected_outpos_i = None
    selected_inpos_i = None
    for outpos_i in range(parent.num_output_positions):
        outpos = parent.output_positions[outpos_i]
        for inpos_i in range(child.num_input_positions):
            inpos = child.input_positions[inpos_i]
            dist = np.linalg.norm(outpos.np() - inpos.np())

            # nasty hack to align vertical strands correctly.
            # only works for knotsize 3
            if outpos_i == len(parent.output_positions):
                if inpos_i != len(parent.output_positions):
                    dist *= 5

            if (
                child.inputs_used[inpos_i] is False
                and parent.outputs_used[outpos_i] is False
            ):
                if smallest_dist is None or dist < smallest_dist:
                    selected_inpos_i = inpos_i
                    selected_inpos = inpos
                    selected_outpos_i = outpos_i
                    selected_outpos = outpos

                    smallest_dist = dist
    if selected_inpos is None:
        print(parent.pos, child.pos)
        print([pos for pos in parent.output_positions])
        print([pos for pos in child.input_positions])
        print([child.inputs_used])
        print([parent.outputs_used])
        raise Exception("didn't find input position")
    if selected_outpos is None:
        raise Exception("didn't find output position")

    if selected_outpos.z < selected_inpos.z:
        logging.debug("invalid z at: child id %s, parent id %s", child.id, parent.id)

    return selected_outpos_i, selected_inpos_i, selected_outpos, selected_inpos


def get_knot_by_id(id, knots):
    for knot in knots:
        if knot.id == id:
            return knot
    raise Exception("Knot id not found")


def weave_graph(links, startknots, knots):
    """
    how it works:
    - start with n bundles and a graph of knots (knots have a xyz
      coordinate, bundles have a start xyz)
    loop:
    - for every bundle get next knot (if not in current knot set)
    - compute bundle target positions (close to future knot)
    - weave until knot
    - weave knot. mark knot as done
    """
    current_set = startknots
    links_down, links_up = links
    # for every output, get connected knot.
    # get position from that knot

    next_knots = []
    stop = False
    while not stop:
        for parent in current_set:
            children = [get_knot_by_id(id, knots) for id in links_down[parent.id]]

            assert len(children) <= len(parent.output_positions), (
                "to many used outputs at a knot%d %d %b",
                len(children),
                len(parent.output_positions),
                parent.knottype == KnotType.startknot,
            )
            logging.debug("weaving for %d", parent.id)
            for child in children:
                if child not in next_knots:
                    next_knots.append(child)

                if True:  # sum(child.inputs_used) < child.num_input_positions:
                    (
                        selected_outpos_i,
                        selected_inpos_i,
                        selected_outpos,
                        selected_inpos,
                    ) = choose_parent_child_link(parent, child)

                    # only draw bundle if preceding knots were already drawn
                    if parent.output_bundles[selected_outpos_i] is not None:
                        weaving.weave_straight_new(
                            parent.output_bundles[selected_outpos_i],
                            selected_outpos,
                            selected_inpos,
                            parent.angle,
                            child.angle,
                        )
                        child.input_bundles[selected_inpos_i] = parent.output_bundles[
                            selected_outpos_i
                        ]
                        child.inputs_used[selected_inpos_i] = True
                        parent.outputs_used[selected_outpos_i] = True

        if len(next_knots) == 0:
            stop = True
        current_set = next_knots

        for knot in next_knots:
            # check if all incoming bundles are already created. unless if its a startknot
            if (
                knot.knottype == KnotType.startknot
                or sum(knot.inputs_used) == knot.num_input_positions
            ):
                # sometimes a knot will start with empty slots. in those cases generate new strands
                for i in range(len(knot.input_bundles)):
                    if knot.inputs_used[i] == False:
                        knot.inputs_used[i] = True
                        knot.input_bundles[i] = utils.generate_strands(4)

                weaving.weave_knot(knot)
        next_knots = []


def add_link(links, parent, child):
    links_down, links_up = links
    links_down[parent.id].append(child.id)
    links_up[child.id].append(parent.id)
    parent.add_output()
    child.add_input()


def count_connections(knots, down_links):
    counter = 0
    for id in down_links.keys():
        counter += len(down_links[id])
    return counter


def strands_from_graph(startknots):
    strands = []
    for knot in startknots:
        for bundle in knot.output_bundles:
            strands += bundle

    # make strands smooth by interpolating space in between
    utils.interpolate_strands(strands, kind="cubic", step_size=0.005)

    return strands
