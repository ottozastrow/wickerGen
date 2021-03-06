import logging
from collections import defaultdict

from weaving import *
from knot import Knot
from utils import interpolate_strands, angle_from_circle_slot


def choose_parent_child_link(parent:Knot, child:Knot):
    # decide which of the childrens inputs to connect to 
    # by choosing the input output position combination with the smalles euclid distance
    smallest_dist = None
    selected_inpos = None
    selected_outpos = None
    selected_outpos_i = None
    selected_inpos_i = None
    
    # if vertical center bundle still unused
    if not parent.outputs_used[-1] and not child.inputs_used[-1]:
        # last one is always the center position.
        selected_inpos_i = child.num_positions -1
        selected_outpos_i = parent.num_positions -1
        selected_outpos = parent.output_positions[selected_outpos_i]
        selected_inpos = child.input_positions[selected_inpos_i]
    else:
        for outpos_i in range(parent.num_positions):
            outpos = parent.output_positions[outpos_i]

            for inpos_i in range(child.num_positions):
                inpos = child.input_positions[inpos_i]
                dist = np.linalg.norm(outpos.np() - inpos.np())
                assert not all(child.inputs_used), "at least one should be free {c}".format(c=child.id)
                # nasty hack to align vertical strands correctly. only works for knotsize 3
                if outpos_i==len(parent.output_positions):
                    if inpos_i !=len(parent.output_positions):
                        dist *= 5
                
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

    return selected_outpos_i, selected_inpos_i, selected_outpos, selected_inpos
    

def get_knot_by_id(id, knots):
    for knot in knots:
        if knot.id == id:
            return knot
    raise Exception("Knot id not found")

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
            children = [get_knot_by_id(id, knots) for id in links_down[parent.id]]
            
            assert len(children) <= len(parent.output_positions), \
                     ("to many used outputs at a knot%d %d %b", len(children), len(parent.output_positions), \
                     parent.knottype==KnotType.startknot)
            # logging.info("weaving for %d %d", parent.id, len(children))
            for child in children:
            
                selected_outpos_i, selected_inpos_i, \
                    selected_outpos, selected_inpos = choose_parent_child_link(parent, child)
                
                # only draw bundle if preceding knots were already drawn 
                if parent.output_bundles[selected_outpos_i] is not None:
                    # logging.info("weaving straight for %d", parent.id)

                    weave_straight_new(
                        parent.output_bundles[selected_outpos_i], 
                        selected_outpos, selected_inpos, parent.angle, child.angle)
                    child.input_bundles[selected_inpos_i] = parent.output_bundles[selected_outpos_i]
                    child.inputs_used[selected_inpos_i] = True
                    parent.outputs_used[selected_outpos_i] = True

                    if child not in next_knots:
                        next_knots.append(child)

        if len(next_knots) == 0:
            stop = True
        current_set = next_knots

        for knot in next_knots:
            # check if all incoming bundles are already created. unless if its a startknot
            if knot.knottype == KnotType.startknot or sum(knot.inputs_used) == knot.num_positions:
                # sometimes a knot will start with empty slots. in those cases generate new strands
                for i in range(len(knot.input_bundles)):
                    if knot.inputs_used[i] == False:
                        knot.inputs_used[i] = True
                        knot.input_bundles[i] = generate_strands(4)
                if any(ib is None for ib in knot.input_bundles):
                    logging.error(knot.id)
                    logging.error(knot.inputs_used)
                    logging.error(knot.input_bundles)
                    raise Exception("at this stage all inputs must be used")
                weave_knot(knot)
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


def generate_circular_knots(num_knots:int, 
                            z_position:float, 
                            radius:float, 
                            knottype, num_strands:int,
                            angle_offset:float) -> list[Knot]:
    knots = []
    angles = np.linspace(0, 2*np.pi -2*np.pi/num_knots, num_knots)
    for el_id in range(num_knots):
        angles_current = angles + angle_from_circle_slot(num_knots, angle_offset)

        x = radius * cos(angles_current[el_id])
        y = radius * sin(angles_current[el_id])
        knot = Knot(knottype, Pos(x,y,z_position), num_strands)
        knots.append(knot)
    return knots


def generate_nice_sample_graph():
    f=1.0 # slim factor
    #layer_radia = [0.9/f, 0.7/f , 0.53/f, 0.64/f, 0.55/f, 0.64/f]  # square
    layer_radia = [1.11/f, 0.78/f , 0.55/f, 0.5/f, 0.53/f, 0.56/f, 0.6, 0.65, 0.72, 0.8]  # round
    # layer_heights = [2.5, 1.8, 1, 0.0, -1, -1.8, -2.6, -3.2, -4, -4.8]
    layer_heights = [h*0.8 for h in range(len(layer_radia), 0, -1)]
    layer_heights = [h*1.2 for h in layer_heights]
    num_elements = 4

    layers = [[] for i in range(len(layer_radia))]
    knots = []
    links = defaultdict(list), defaultdict(list)  # will return [] instead of key error

    
    layer_radius = layer_radia[0]
    start_knots_diagonal = generate_circular_knots(num_elements*2, layer_heights[0], layer_radia[0], 
                                         KnotType.startknot, 4,
                                         angle_from_circle_slot(num_elements*2, 0.5))
    layers[0] = start_knots_diagonal

    start_knots_vertical = generate_circular_knots(num_elements*2, layer_heights[0], layer_radia[0], 
                                         KnotType.startknot, 4,
                                         angle_from_circle_slot(num_elements*2, 0.0))

    center_knots = [Knot(KnotType.startknot, Pos(0,0,h)) for h in layer_heights]
    startknots = start_knots_diagonal + start_knots_vertical + [center_knots[0]]
    knots += startknots
    knots += center_knots

    
    for l in range(1, len(layer_radia)):
        layer_radius = layer_radia[l]
        angles = np.linspace(0, 2*np.pi -2*np.pi/num_elements, num_elements)

        for el_id in range(num_elements):
            angles_current = angles + angle_from_circle_slot(num_elements, l / 2)
            x = layer_radius * cos(angles_current[el_id])
            y = layer_radius * sin(angles_current[el_id])
            knottype = [KnotType.move2, KnotType.move4, KnotType.move1][el_id%3]
            knottype = KnotType.move2
            knot = Knot(knottype, Pos(x,y,layer_heights[l]))
            knots.append(knot)
            layers[l].append(knot)

            if l==1:
                parent1 = start_knots_diagonal[(el_id*2)%(num_elements*2)]
                parent2 = start_knots_diagonal[(el_id*2+1)%(num_elements*2)]
                parent3 = start_knots_vertical[(el_id*2+1)%(num_elements*2)]
            
                
            elif l==2:
                parent1 = layers[l-1][(el_id+1)%(num_elements)]
                parent2 = layers[l-1][(el_id)%(num_elements)]
                parent3 = start_knots_vertical[(el_id*2+2)%(num_elements*2)]

            else: # >2
                parent1 = layers[l-1][(el_id+1)%(num_elements)]
                parent2 = layers[l-1][(el_id)%(num_elements)]
                parent3 = layers[l-2][(el_id+1) % num_elements]
            
            if l%2:
                add_link(links, center_knots[l-1], knot)
            else:
                add_link(links, layers[l-1][el_id], center_knots[l])
            add_link(links, parent1, knot)
            add_link(links, parent2, knot)
            add_link(links, parent3, knot)

        add_link(links, center_knots[l-1], center_knots[l])
    
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

    add_link(links, startknots[0],k1)
    add_link(links, startknots[1],k1)
    add_link(links, startknots[8],k1)
    add_link(links, startknots[2],k2)
    add_link(links, startknots[3],k2)
    add_link(links, k1, k4)
    add_link(links, k1, k3)
    add_link(links, k2, k4)
    add_link(links, startknots[6], k3)
    add_link(links, k3, k5)
    add_link(links, k4, k5)
    add_link(links, k1,k5)

    return links, startknots, knots


def generate_knot_graph(inputs:int=2):
    top_knots = generate_circular_knots(inputs, 1.6, 0.3, KnotType.startknot, 4, 0)
    middle_knot_top = Knot(KnotType.startknot, Pos(0,0,1.6), 4)
    middle_knot = Knot(KnotType.move2, Pos(0,0,0.8))
    middle_knot_bottom = Knot(KnotType.move2, Pos(0,0,0.0))

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



def strands_from_graph(startknots):
    strands = []
    for knot in startknots:
        for bundle in knot.output_bundles:
            strands += bundle
    
    # make strands smooth by interpolating space in between
    interpolate_strands(strands, kind="cubic", step_size=0.005)

    return strands

def find_startknots(knots, links) -> list[Knot]:
    """Return knots without parents."""
    _, links_up = links
    startknots = []
    for knot in knots:
        if len(links_up[knot.id]) == 0:
            startknots.append(knot)
    return startknots