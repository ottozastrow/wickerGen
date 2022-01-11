import numpy as np
from util_classes import *
from utils import *


def test_rotate():
    origin = Pos(1, 2, 3)
    point = Pos(2, 3, 3)
    rotate(origin, point, np.pi)
    point.x = np.around(point.x, 3)
    assert point.x == 0
