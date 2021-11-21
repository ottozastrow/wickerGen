from numpy import arctan
from util_classes import *
from knot_types import Mappings, KnotType
from utils import rotate

class Knot:
    """
    each knot has a position in 3d space. 
    it also provides the locations of input and output bundles
    """
    knot_count = 0
    def generate_strands(self):
        self.strands = [Strand(i) for i in range(4)]

    def __init__(self, knottype, pos:Pos):
        self.knottype = knottype
        self.pos = pos
        
        self.height = len(knottype) * Arena.knot_cycle_height  # TODO: find better way to determine height. this is not safe.
        self.centers = [Pos(self.pos.x - Arena.bundle_radius, self.pos.y, self.pos.z), 
                        self.pos,
                        Pos(self.pos.x + Arena.bundle_radius, self.pos.y, self.pos.z)]
        if knottype is KnotType.startknot:
            self.output_bundles = [[Strand(i) for i in range(4)]]
            self.output_positions = [pos]
        else:
            self.output_bundles = [None, None]
            self.input_positions = [
                Pos(self.centers[0].x, self.centers[0].y, self.centers[0].z + self.height/2),
                Pos(self.centers[2].x, self.centers[2].y, self.centers[2].z + self.height/2)
            ]
            self.output_positions = [
                Pos(self.centers[0].x, self.centers[0].y, self.centers[0].z - self.height/2),
                Pos(self.centers[2].x, self.centers[2].y, self.centers[2].z - self.height/2)
            ]
        self.angle = 0
        self.input_bundles = [None, None]        
        self.outputs_used = [False, False]
        self.inputs_used = [False, False]
        self.id = Knot.knot_count
        Knot.knot_count += 1


    def align_orientation(self, parents):
        # update centers, input and output positions
        if len(parents) > 2:
            raise Exception("not supported yet. knot must have two parents")
        
        elif len(parents) == 2:
            angle = np.arctan2(
                (parents[1].pos.x - parents[0].pos.x),
                (parents[1].pos.y - parents[0].pos.y),
                )
            # parent.position - self.position is the orientation. cancel out z.
        elif len(parents) == 1:
            angle = np.arctan2((parents[0].pos.x - self.pos.x), 
                               (parents[0].pos.y - self.pos.y))
        else: # incase no parents are set no orientation needs to be changed
            return

        # hacky solution. Coordinate frame of rotate function doesnt match wickerGen coordinate frame
        angle*=-1
        angle += np.pi/2
        
        self.angle = angle

        for point in self.input_positions:
            rotate(self.pos, point, angle)
        for point in self.output_positions:
            rotate(self.pos, point, angle)
        for point in self.centers:
            rotate(self.pos, point, angle)

