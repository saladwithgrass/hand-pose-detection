import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.append('../')
from utils.draw_utils import load_colors, load_connections
class Visualizer3D():
    
    def __init__(self):
        
        # add space to draw
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # set axis parameters
        self.MAX_DIM = 200
        self.X_CENTER = 0
        self.Y_CENTER = 0
        self.Z_CENTER = 200
        
        # load hand connections
        self.hierarchy_dict = load_connections('../config/hand_connections.json')
        # load finger colors
        self.color_dict = load_colors('../config/hand_colors.json', '../config/hand_connections.json')

        # prepare axes 
        self.set_axes()
        
    def set_axes(self):
        # set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        # set limits
        self.ax.set_xlim3d([-self.MAX_DIM + self.X_CENTER, self.MAX_DIM + self.X_CENTER])
        self.ax.set_ylim3d([-self.MAX_DIM + self.Y_CENTER, self.MAX_DIM + self.Y_CENTER])
        self.ax.set_zlim3d([-self.MAX_DIM + self.Z_CENTER, self.MAX_DIM + self.Z_CENTER])

    def draw_hand(self, landmarks):
        # check if there's something to be drawn
        if len(landmarks) == 0:
            return
        landmarks = np.array(landmarks)
        # make wrist cyclical
        # draw in each color
        for color, indexes in self.color_dict.items():
            cur_vectors = landmarks[indexes]
            self.ax.plot(
                xs=-cur_vectors[:, 0],
                ys=cur_vectors[:, 1],
                zs=-cur_vectors[:, 2],
                color=color,
                marker='o'
                )

    def draw_coordinates(self, axes, center):
        # extract axes
        x_axis = axes[0]*50 + center
        y_axis = axes[1]*50 + center
        z_axis = axes[2]*50 + center

        # draw x axis
        self.ax.plot(
            xs=[-center[0], -x_axis[0]],
            ys=[center[1], x_axis[1]],
            zs=[-center[2], -x_axis[2]],
            color="red"
        )

        # draw y axis
        self.ax.plot(
            xs=[-center[0], -y_axis[0]],
            ys=[center[1], y_axis[1]],
            zs=[-center[2], -y_axis[2]],
            color="green"
        )

        # draw z axis
        self.ax.plot(
            xs=[-center[0], -z_axis[0]],
            ys=[center[1], z_axis[1]],
            zs=[-center[2], -z_axis[2]],
            color="blue"
        )

    def update_points(self, joint_coordinates=None, axes=None, axes_center=None, pause = 0.01, cameras=None, camera_colors=None):
        """
        Takes and array of 3d vectors with point coordinates.
        Updates plot.
        """

        # clear previous drawings
        self.ax.cla()

        # draw end effector orientation
        if axes is not None and axes_center is not None:
            self.draw_coordinates(axes, axes_center)

        # draw the hand if it is needed
        if joint_coordinates is not None:
            self.draw_hand(joint_coordinates) 

        # draw cameras if they exist
        if cameras is not None:
            if camera_colors is None:
                camera_colors = ['red'] * len(cameras)
            total_cameras = len(cameras)
            cameras = np.array(cameras).T
            for camera_idx in range(total_cameras):
                cam_xs = cameras[0][camera_idx]
                cam_ys = cameras[1][camera_idx]
                cam_zs = cameras[2][camera_idx]
                self.ax.plot(xs=cam_xs, ys=cam_ys, zs=cam_zs, color=camera_colors[camera_idx], marker='x', linestyle='None')
        
        self.set_axes()
        plt.pause(pause)