from utils import *
import numpy as np

import matplotlib.pyplot as plt

num_slots = 4
circle_points(num_slots, 0, 0)
x,y = circle_points(num_slots, 0, Arena.bundle_radius * 1.1)
x_inner,y_inner = circle_points(num_slots, (np.pi*2) / num_slots / 2, Arena.bundle_radius * 0.8)
x_outer,y_outer = circle_points(num_slots, (np.pi*2) / num_slots / 2, Arena.bundle_radius * 1.1)
n = 3
plt.scatter(x[:n],y[:n], color="yellow")
plt.scatter(x_inner[:n],y_inner[:n], color="red")
plt.scatter(x_outer[:n],y_outer[:n], color="blue")
plt.show()

