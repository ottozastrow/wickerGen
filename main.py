"""
input a set of curves and points, output robot movement
MVP: 
plot movement. 
input starting points and connections from GH file
knot logic without limiations of horngears.
- distinguish between knot type and movement.
- a knot type takes bundles as input and outputs new bundles.
- initially all bundles consist of 4 strands
- later bundles might have 4,8,12, strand (like 4, but side-by-side)
"""

import matplotlib.pyplot as plt
import numpy as np
import logging, sys

from visualize import *
from graph import *


if __name__ =="__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    # links, startknots, knots = generate_nice_sample_graph()
    links, startknots, knots = generate_sample_graph()
    weave_graph(links, startknots, knots)

    plot_3d_strands(strands_from_graph(startknots))
