from codecs import strict_errors
from collections import defaultdict
from knot import Knot
from util_classes import KnotType, Pos
from graph import add_link, find_startknots


def load_graph_from_file(path):
    """Load graph from obj file.
    This file must contain lines made up of two vertices."""
    f = open(path, "r")
    lines = []
    linecount = 0
    vertices = []
    all_str_vertices = set()
    for l in f:
        if l.startswith("v"):
            vertices.append(l[2:-2])
            all_str_vertices.add(l[2:-2])

        elif l.startswith("end"):
            lines.append(vertices)
            vertices = []
        linecount += 1

    # create a knot for every unique vertice
    # create a mapping between vertice_string and knot
    vertice_knot_mappings = {}
    for str in all_str_vertices:
        if str not in vertice_knot_mappings.keys():
            vertice_pts =  [float(pt) for pt in str.split(" ")]
            vertice_pts = [vertice_pts[0]*1.2, vertice_pts[2]*1.2, vertice_pts[1]*2]
            knot = Knot(knottype=KnotType.move2, pos=Pos(*vertice_pts))
            vertice_knot_mappings[str] = knot

    knots = vertice_knot_mappings.values()    

    # create links between all knots
    links = defaultdict(list), defaultdict(list)
    for a, b in lines:
        vertice_a = vertice_knot_mappings[a]
        vertice_b = vertice_knot_mappings[b]

        # the higher z position should be the first vertice
        if vertice_a.pos.z > vertice_b.pos.z:
            add_link(links, vertice_a, vertice_b)
        else:
            add_link(links, vertice_b, vertice_a)
    
    startknots = find_startknots(knots, links)
    for knot in knots:
        if knot in startknots:
            knot.knottype = KnotType.startknot
    return links, startknots, knots
