
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
    
    def np(self):
        return np.array([self.x, self.y, self.z])

class Strand:
    def __init__(self, slot):
        self.slot = slot        # position index within bundle
        self.knot_slot = slot   # position index within several bundles
        self.x = []
        self.y = []
        self.z = []

    def interpolate(self, divide_steps):
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
    divide_steps = 2
    interpolate_steps = 6
    ellipse_a = 0.02
    ellipse_b = 0.01
    bundle_radius = ellipse_b * 2 *1.5 # second *2 is only for nicer optics TODO: Remove
    weave_cycle_height = 0.08
