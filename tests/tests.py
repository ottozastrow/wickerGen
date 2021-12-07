from utils import * 
from util_classes import * 
import numpy as np

def test_rotate():
    origin = Pos(1, 2, 3)
    point = Pos(2, 3, 3)
    rotate(origin, point, np.pi)
    point.x = np.around(point.x, 3)
    assert point.x == 0