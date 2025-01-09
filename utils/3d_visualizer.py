import matplotlib.pyplot as plt
import numpy as np

class HandDrawer():
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def update_points(self, joint_coordinates):
        # clear previous drawings
        self.ax.cla()

        # convert points 
        xs = joint_coordinates[::, 0]
        ys = joint_coordinates[::, 1]
        zs = joint_coordinates[::, 2]

        # plot points
        self.ax.plot(xs=xs, ys=ys, zs=zs, marker='o')
