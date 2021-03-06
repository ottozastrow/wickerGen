import numpy as np

from .util_classes import Arena, KnotType, Pos
from .utils import generate_circular_positions, generate_strands, rotate


class Knot:
    """
    each knot has a position in 3d space.
    it also provides the locations and references of input and output bundles
    """

    knot_count = 0

    def __init__(self, knottype, pos: Pos, num_strands: int = 4):
        self.knottype = knottype
        self.pos = pos

        self.angle = 0
        self.num_strands = num_strands

        self.id = Knot.knot_count
        Knot.knot_count += 1
        self.num_output_positions = 0
        self.num_input_positions = 0

    def add_output(self) -> None:
        self.num_output_positions += 1

    def add_input(self) -> None:
        self.num_input_positions += 1

    def initialize_knot_slots(self, parents):
        """initialize knot slots after all connections are known"""
        """inputs and output positions are arranged in a circle around the knot center
        if the number of connections is uneven we add a center position
        """
        self.input_positions = []
        self.output_positions = []

        self.num_input_positions = len(parents)
        self.num_positions = max(self.num_input_positions, self.num_output_positions)

        if self.knottype is KnotType.startknot:
            self.output_bundles = [
                generate_strands(self.num_strands) for i in range(self.num_positions)
            ]
        else:
            self.output_bundles = [None for i in range(self.num_positions)]
        self.height = Arena.knot_cycle_height * np.sqrt(len(parents))
        
        # add circular positions
        if self.num_positions > 1:
            knot_positions = self.num_positions - 1
            self.input_positions += generate_circular_positions(
                self.pos,
                knot_positions,
                self.pos.z + self.height / 2 * 1.2,  # 1.2 is nasty hack
                Arena.knot_bundle_distance,
                0,
            )
            self.output_positions += generate_circular_positions(
                self.pos,
                knot_positions,
                self.pos.z - self.height / 2,
                Arena.knot_bundle_distance,
                0,
            )
        # add center position
        self.input_positions.append(
            Pos(self.pos.x, self.pos.y, self.pos.z + self.height / 2 * 1.2)
        )  # 1.2 is nasty hack
        self.output_positions.append(
            Pos(self.pos.x, self.pos.y, self.pos.z - self.height / 2)
        )

        self.input_bundles = [None for i in range(self.num_positions)]      
        self.inputs_used = [False for i in range(self.num_positions)]
        self.outputs_used = [False for i in range(self.num_positions)]

    def align_orientation(self, parents):
        """orientation of knot is made dependant on parents"""
        if len(parents) >= 2:
            angle = np.arctan2(
                (parents[1].pos.x - parents[0].pos.x),
                (parents[1].pos.y - parents[0].pos.y),
            )
            # parent.position - self.position is the orientation. cancel out z.
        elif len(parents) == 1:
            angle = np.arctan2(
                (parents[0].pos.x - self.pos.x), (parents[0].pos.y - self.pos.y)
            )
        else:  # incase no parents are set no orientation needs to be changed
            return

        # hacky solution. Coordinate frame of
        # rotate function doesnt match wickerGen coordinate frame
        angle *= -1
        angle += np.pi / 2

        self.angle = angle
        for point in self.input_positions:
            rotate(self.pos, point, angle)
        for point in self.output_positions:
            rotate(self.pos, point, angle)
