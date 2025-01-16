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
        self.ax.set_zlim3d([-self.MAX_DIM*5, self.MAX_DIM*5])
    
    def update_points(self, joint_coordinates, pause = 0.01, cameras=None, camera_colors=None):
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
        if cameras is not None:
            if camera_colors is None:
                camera_colors = ['red'] * len(cameras)
            total_cameras = len(cameras)
            cameras = np.array(cameras).T
            print(cameras)
            for camera_idx in range(total_cameras):
                cam_xs = cameras[0][camera_idx]
                cam_ys = cameras[1][camera_idx]
                cam_zs = cameras[2][camera_idx]
                self.ax.plot(xs=cam_xs, ys=cam_ys, zs=cam_zs, color=camera_colors[camera_idx], marker='x')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_ylim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_zlim3d([-self.MAX_DIM*5, self.MAX_DIM*5])
        plt.pause(pause)