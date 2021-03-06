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

import argparse
import logging
import sys

from braidGenerator import graph, util_classes, visualize
from modelBuilder import models

parser = argparse.ArgumentParser()
parser.add_argument(
    "--show3d",
    action="store_true",
    help="plots entire model with individual strands in 3d",
)
parser.add_argument(
    "--animate", action="store_true", help="plots 2d animation of strand movement"
)
parser.add_argument(
    "--showcombined", action="store_true", help="plots 3d model and robot floor"
)
parser.add_argument(
    "--showgraph", action="store_true", help="shows graph network before weaving"
)

parser.add_argument("--smallmodel", action="store_true", help="plots smaller model")
parser.add_argument("--save_to_file", action="store_true", help="saves in html file")
parser.add_argument(
    "--obj_path",
    type=str,
    default=None,
    help="saves in braided 3d lines model as obj file",
)
parser.add_argument(
    "--animatesteps", type=int, default=50, help="number of frames for animation"
)


args = parser.parse_args()
util_classes.Arena.animation_steps = args.animatesteps

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    if args.smallmodel:
        # links, startknots, knots = generate_sample_graph()
        links, startknots, knots = models.generate_knot_graph()
    else:
        links, startknots, knots = models.generate_nice_sample_graph()

    for knot in knots:
        parents = [graph.get_knot_by_id(id, knots) for id in links[1][knot.id]]
        knot.initialize_knot_slots(parents)
        knot.align_orientation(parents)

    if args.showgraph:
        visualize.plot_graph(knots, links)

    graph.weave_graph(links, startknots, knots)

    strands = graph.strands_from_graph(startknots)
    if args.show3d:
        visualize.plot_3d_strands(strands, args.save_to_file)

    if args.obj_path is not None:
        visualize.write_obj_file(strands, args.obj_path)

    if args.animate:
        if False:  # will show extrapolated robot position
            animated_strands_2d = visualize.calc_2d_robot_plane(strands)
            visualize.plot_animated_strands(animated_strands_2d, save=args.save_to_file)
        else:
            visualize.plot_animated_strands(strands, save=args.save_to_file)

    if args.showcombined:
        animated_strands_3d = visualize.calc_3d_robot_plane(strands)
        visualize.plot_3d_animated_strands(animated_strands_3d, save=args.save_to_file)
