
import numpy as np
from scipy import interpolate



class Pos:
    def __init__(self, x: float, y: float, z: float, label=""):
        self.x = x
        self.y = y
        self.z = z
        self.label=label
    
    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
    
    def __str__(self):
        return str((self.x, self.y, self.z, self.label))
    
    def np(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])


class KnotType:
    """different knot types are currently not supported"""
    move1 = [None]
    move2 = [None]
    move3 = [None]
    move4 = [None]
    startknot = []


class Strand:
    def __init__(self, slot):
        self.slot = slot        # position index within bundle
        self.knot_slot = slot   # position index within several bundles
        self.x = []
        self.y = []
        self.z = []
    
    def interpolate(self, divide_steps: int):
        # make strands smooth by interpolating space in between

        if len(self.x)>0:
            x = np.array(self.x)
            y = np.array(self.y)
            z = np.array(self.z)
            fx = interpolate.interp1d(z, x, kind="cubic")
            fy = interpolate.interp1d(z, y, kind='cubic')
            newz = np.linspace(min(z), max(z), len(z)*divide_steps)
            xnew = fx(newz)   # use interpolation function returned by `interp1d`
            ynew = fy(newz)   # use interpolation function returned by `interp1d`
            self.x = list(xnew)
            self.y = list(ynew)
            self.z = list(newz)



class Arena:
    """globally useful configs"""
    animation_steps = 5
    
    divide_steps = 1
    divide_knot_steps = 2
    interpolate_steps = 12
    straight_braid_radius = 0.02
    knot_bundle_distance = 0.07
    knot_gridsize_y = 0.04
    knot_gridsize_x = 0.01
    weave_cycle_height = 0.06
    knot_cycle_height = 0.04
    strand_width = 0.004  # including some padding

    interpolate_steps_per_meter = 0.005
