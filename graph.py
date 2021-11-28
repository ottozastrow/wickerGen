import logging
from collections import defaultdict

from weaving import *
from knot import Knot
from utils import interpolate_strands

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
            assert len(children) <= len(parent.output_positions), ("to many used outputs at a knot%d %d %b", len(children), len(parent.output_positions), \
                     parent.knottype==KnotType.startknot)
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

                        # nasty hack to align vertical strands correctly. only works for knotsize 3
                        if outpos_i==1:
                            if inpos_i !=1:
                                dist *= 4
                        

                        if child.inputs_used[inpos_i] is False and parent.outputs_used[outpos_i] is False:
                            if smallest_dist is None or dist<smallest_dist:
                                selected_inpos_i = inpos_i
                                selected_inpos = inpos
                                selected_outpos_i = outpos_i
                                selected_outpos = outpos
                                
                                smallest_dist = dist
                if selected_inpos is None:
                    raise Exception("didn't find input position")
                if selected_outpos is None:
                    raise Exception("didn't find output position")

                if selected_outpos.z < selected_inpos.z:
                    logging.debug("invalid z at: child id %s, parent id %s", child.id, parent.id)

                # only draw bundle if preceding knots were already drawn 
                if parent.output_bundles[selected_outpos_i] is not None:
                    weave_straight_new(
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
            if knot.knottype == KnotType.startknot or sum(knot.inputs_used) == knot.num_input_positions:
                # sometimes a knot will start with empty slots. in those cases generate new strands
                for i in range(len(knot.input_bundles)):
                    if knot.inputs_used[i] == False:
                        knot.inputs_used[i] = True
                        knot.input_bundles[i] = generate_strands(4)
                
                weave_knot(knot)
        next_knots = []
    

def add_link(knots, links, parent, child):
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

def generate_nice_sample_graph():
    layer_radia = [1.2, 0.83 , 0.6, 0.66, 0.8, 0.9]
    layer_heights = [2.4, 1.7, 1, 0.0, -1, -1.8]

    num_elements = 3

    layers = [[] for i in range(len(layer_radia))]
    knots = []
    startknots = []
    links = defaultdict(list), defaultdict(list)  # will return [] instead of key error

    
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

    # straight startknots
    straight_start_knots = []
    angles = np.linspace(0, 2*np.pi -2*np.pi/(num_elements*2), num_elements*2)
    for el_id in range(num_elements*2):
        x = layer_radius * cos(angles[el_id])
        y = layer_radius * sin(angles[el_id])
        knot = Knot(KnotType.startknot, Pos(x,y,layer_heights[0]), num_strands=8)
        startknots.append(knot)
        knots.append(knot)
        straight_start_knots.append(knot)

    
    for l in range(1, len(layer_radia)):
        layer_radius = layer_radia[l]

        angles = np.linspace(0, 2*np.pi -2*np.pi/num_elements, num_elements)
        for el_id in range(num_elements):
            angles_current = angles + (l)*2*np.pi / num_elements / 2
            x = layer_radius * cos(angles_current[el_id])
            y = layer_radius * sin(angles_current[el_id])
            knottype = [KnotType.move2, KnotType.move4, KnotType.move1][el_id%3]
            knottype = KnotType.move2
            knot = Knot(knottype, Pos(x,y,layer_heights[l]))
            knots.append(knot)
            layers[l].append(knot)
            if l==1:
                parent1 = layers[l-1][(el_id*2)%(num_elements*2)]
                parent2 = layers[l-1][(el_id*2+1)%(num_elements*2)]
                parent3 = straight_start_knots[(el_id*2+1)%(num_elements*2)]
                
            elif l==2:
                parent1 = layers[l-1][(el_id+1)%(num_elements)]
                parent2 = layers[l-1][(el_id)%(num_elements)]
                parent3 = straight_start_knots[(el_id*2+2)%(num_elements*2)]

            else: # >2
                parent1 = layers[l-1][(el_id+1)%(num_elements)]
                parent2 = layers[l-1][(el_id)%(num_elements)]
                parent3 = layers[l-2][(el_id+1) % num_elements]

            add_link(knots, links, parent1, knot)
            add_link(knots, links, parent2, knot)
            add_link(knots, links, parent3, knot)

    
    return links, startknots, knots


def generate_sample_graph():
    """ dummy function for testing"""
    startknots = [
            Knot(KnotType.startknot, Pos(0.0*3, 0.1, 0.8)),
            Knot(KnotType.startknot, Pos(0.13*3, 0.05, 0.8)),
            Knot(KnotType.startknot, Pos(0.17*3, 0.05, 0.8)),
            Knot(KnotType.startknot, Pos(0.3*3, 0.1, 0.8)),

            Knot(KnotType.startknot, Pos(0.0*3, 0.0, 0.0)),
            Knot(KnotType.startknot, Pos(0.3*3, 0.0, 0.0)),
            Knot(KnotType.startknot, Pos(-0.13*3, 0.0, 0.4)),
            Knot(KnotType.startknot, Pos(1, 0.2, 0.8)),

            Knot(KnotType.startknot, Pos(0.15, 0.0, 0.8)),
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

    links = defaultdict(list), defaultdict(list)

    add_link(knots, links, startknots[0],k1)
    add_link(knots, links, startknots[1],k1)
    add_link(knots, links, startknots[8],k1)
    add_link(knots, links, startknots[2],k2)
    add_link(knots, links, startknots[3],k2)
    add_link(knots, links, k1, k4)
    add_link(knots, links, k1, k3)
    add_link(knots, links, k2, k4)
    add_link(knots, links, startknots[6], k3)
    add_link(knots, links, k3, k5)
    add_link(knots, links, k4, k5)
    add_link(knots, links, k1,k5)

    return links, startknots, knots

def generate_prototype_graph():

    startknot_positions = np.meshgrid(np.linspace())


def strands_from_graph(startknots):
    strands = []
    for knot in startknots:
        for bundle in knot.output_bundles:
            strands += bundle
    
    # make strands smooth by interpolating space in between
    interpolate_strands(strands, kind="cubic", step_size=0.005)

    return strands