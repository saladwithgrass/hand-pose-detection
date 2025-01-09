import matplotlib.pyplot as plt
import numpy as np

class Visualizer3D():
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
    
    def update_points(self, joint_coordinates):
        """
        Takes and array of 3d vectors with point coordinates.
        Updates plot.
        """

        # clear previous drawings
        self.ax.cla()

        # convert points 
        joint_coordinates = np.array(joint_coordinates).T[0]
        xs = joint_coordinates[0]
        ys = joint_coordinates[1]
        zs = joint_coordinates[2]

        # plot points
        self.ax.plot(xs=xs, ys=ys, zs=zs, marker='o')
        plt.pause(0.01)
