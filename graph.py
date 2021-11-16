import logging

from scipy import interpolate
from weaving import *
from knot import Knot

def weave_graph(links, startknots, knots):
    """
    how it works:
    - start with n bundles and a graph of knots (knots have a xyz coordinate, bundles have a start xyz)
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
            
            children = [knots[i] for i in links_down[parent.id]]
            assert len(children) <= len(parent.output_positions), ("to many used outputs at a knot%d", len(children))
            logging.debug("weaving for %d", parent.id)

            for child in children:
                if child not in next_knots:
                    next_knots.append(child)
                
                # decide which of the childrens inputs to connect to 
                # by choosing the input output position combination with the smalles euclid distance
                smallest_dist = None
                selected_inpos = None
                selected_outpos = None
                for outpos_i in range(len(parent.output_positions)):
                    outpos = parent.output_positions[outpos_i]
                    for inpos_i in range(len(child.input_positions)):
                        inpos = child.input_positions[inpos_i]
                        dist = np.linalg.norm(outpos.np() - inpos.np())
                        if child.inputs_used[inpos_i] is False and parent.outputs_used[outpos_i] is False:
                            if smallest_dist is None or dist<smallest_dist:
                                selected_inpos_i = inpos_i
                                selected_inpos = inpos
                                selected_outpos_i = outpos_i
                                selected_outpos = outpos
                                
                                smallest_dist = dist
                        # Todo mark inpos and outpos as occupied and prevent double use
                if selected_inpos is None or selected_outpos is None:
                    raise Exception("didn't find position")

                if selected_outpos.z < selected_inpos.z:
                    logging.debug("invalid z at: child id %s, parent id %s", child.id, parent.id)

                # only draw bundle if preceding knots were already drawn 
                if parent.output_bundles[selected_outpos_i] is not None:
                    weave_straight(
                        parent.output_bundles[selected_outpos_i], 
                        selected_outpos, selected_inpos, parent.angle, child.angle)
                    child.input_bundles[selected_inpos_i] = parent.output_bundles[selected_outpos_i]
                    child.inputs_used[selected_inpos_i] = True
                    parent.outputs_used[selected_outpos_i] = True

        if len(next_knots) == 0:
            stop = True
        current_set = next_knots

        for knot in next_knots:
            # check if all incoming bundles are already created. unless if its a startknot
            if knot.knottype == KnotType.startknot or all(knot.inputs_used):
                weave_knot(knot)
        next_knots = []
    

def add_link(knots, links, parent, child):
    # print(parent.output_positions[0].z, child.input_positions[0].z)
    assert parent.output_positions[0].z >= child.input_positions[0].z, child.id
    
    links_down, links_up = links
    links_down[parent.id].append(child.id)
    links_up[child.id].append(parent.id)

    all_parents = [knots[id] for id in links_up[child.id]]


def count_connections(knots, down_links):
    counter = 0
    for id in down_links.keys():
        counter += len(down_links[id])
    return counter



def generate_nice_sample_graph():
    layer_radia = [1.2, 0.83, 0.6, 0.66, 0.8, 0.9]
    layers = [[] for i in range(len(layer_radia))]
    layer_heights = [1.8, 1.2, 0.6, 0.0, -0.6, -1.2]
    num_elements = 6
    knots = []
    startknots = []
    links_down, links_up = {}, {}
    links = (links_down, links_up)
    for knot_id in range((num_elements+2) * len(layer_radia)):
        links_down[knot_id] = []
        links_up[knot_id] = []
    
    layer_radius = layer_radia[0]
    angles = np.linspace(0, 2*np.pi -2*np.pi/(num_elements*2), num_elements*2)
    for el_id in range(num_elements*2):
        angles_current = angles + 2*np.pi / (num_elements*2) / 2

        x = layer_radius * cos(angles_current[el_id])
        y = layer_radius * sin(angles_current[el_id])
        knot = Knot(KnotType.startknot, Pos(x,y,layer_heights[0]))
        startknots.append(knot)
        knots.append(knot)
        layers[0].append(knot)


    for l in range(1, len(layer_radia)):
        layer_radius = layer_radia[l]

        angles = np.linspace(0, 2*np.pi -2*np.pi/num_elements, num_elements)
        for el_id in range(num_elements):
            angles_current = angles + (l)*2*np.pi / num_elements / 2
            x = layer_radius * cos(angles_current[el_id])
            y = layer_radius * sin(angles_current[el_id])
            knottype = [KnotType.move2, KnotType.move4, KnotType.move1][el_id%3]
            knot = Knot(knottype, Pos(x,y,layer_heights[l]))
            knots.append(knot)
            layers[l].append(knot)
            if l==1:
                parent1 = layers[l-1][(el_id*2)%(num_elements*2)]
                parent2 = layers[l-1][(el_id*2+1)%(num_elements*2)]
            else:
                parent1 = layers[l-1][(el_id+1)%(num_elements)]
                parent2 = layers[l-1][(el_id)%(num_elements)]
            add_link(knots, links, parent1, knot)
            add_link(knots, links, parent2, knot)



    for knot in knots:
        parents = [knots[id] for id in links_up[knot.id]]
        knot.align_orientation(parents)
    return (links_down, links_up), startknots, knots
        



def generate_sample_graph():
    """ dummy function for testing"""
    startknots = [
            Knot(KnotType.startknot, Pos(0.0*3, 0.1, 0.8)),
            Knot(KnotType.startknot, Pos(0.13*3, 0.25, 0.8)),
            Knot(KnotType.startknot, Pos(0.17*3, 0.25, 0.8)),
            Knot(KnotType.startknot, Pos(0.3*3, 0.1, 0.8)),

            Knot(KnotType.startknot, Pos(0.0*3, 0.0, 0.0)),
            Knot(KnotType.startknot, Pos(0.3*3, 0.0, 0.0)),
            Knot(KnotType.startknot, Pos(-0.13*3, 0.0, 0.4)),
            Knot(KnotType.startknot, Pos(1, 0.2, 0.8)),
        ]
    k1 = Knot(KnotType.move2, Pos(0.05*3, 0 , 0.4))
    k2 = Knot(KnotType.move4, Pos(0.25*3, 0 , 0.4))

    k3 = Knot(KnotType.move2, Pos(0.0*3, 0, -0.1))
    k4 = Knot(KnotType.move2, Pos(0.15*3, 0.0, -0.1))

    k5 = Knot(KnotType.move2, Pos(0.05*3, 0.4, -0.5))
    k6 = Knot(KnotType.move2, Pos(0.25*3, 0.4, -0.5))
    # k7 = Knot(KnotType.move2, Pos(0.9, 0.6, 0.4))
    # k8 = Knot(KnotType.move2, Pos(0.8, 0.4, 0.0))
    knots = startknots + [k1, k2, k3, k4, k5, k6]

    links_down, links_up = {}, {}
    links = (links_down, links_up)
    for knot in knots:
        links_down[knot.id] = []
        links_up[knot.id] = []

    add_link(knots, links, startknots[0],k1)
    add_link(knots, links, startknots[1],k1)
    add_link(knots, links, startknots[2],k2)
    add_link(knots, links, startknots[3],k2)
    add_link(knots, links, k1, k4)
    add_link(knots, links, k1, k3)
    add_link(knots, links, k2, k4)
    add_link(knots, links, startknots[6], k3)
    add_link(knots, links, k3, k5)
    add_link(knots, links, k4, k5)

    for knot in knots:
        parents = [knots[id] for id in links_up[knot.id]]
        knot.align_orientation(parents)

    return (links_down, links_up), startknots, knots

def strands_from_graph(startknots):
    strands = []
    for knot in startknots:
        for bundle in knot.output_bundles:
            strands += bundle

    # make strands smooth by interpolating space in between
    for strand in strands:
        strand.interpolate(Arena.interpolate_steps)

    return strands