import matplotlib.pyplot as plt
import numpy as np

class Visualizer3D():
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.MAX_DIM = 500

        self.ax.set_xlim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_ylim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_zlim3d([-self.MAX_DIM, self.MAX_DIM])
    
    def update_points(self, joint_coordinates, pause = 0.001):
        """
        Takes and array of 3d vectors with point coordinates.
        Updates plot.
        """

        # clear previous drawings
        self.ax.cla()

        # convert points 
        joint_coordinates = np.array(joint_coordinates).T
        xs = joint_coordinates[0]
        ys = joint_coordinates[1]
        zs = joint_coordinates[2]

        # plot points
        self.ax.plot(xs=xs, ys=ys, zs=zs, marker='o')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_ylim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_zlim3d([-self.MAX_DIM, self.MAX_DIM])
        plt.pause(pause)