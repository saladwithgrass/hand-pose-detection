import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.append('../')
from utils.draw_utils import load_colors, load_connections
class Visualizer3D():
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.MAX_DIM = 200
        self.Z_OFFSET = 0

        # load hand connections
        self.hierarchy_dict = load_connections('../config/hand_connections.json')
        # load finger colors
        self.color_dict = load_colors('../config/hand_colors.json', '../config/hand_connections.json')
        # convert colors to matplotlib
        max_color = 255.0
        
        print(self.hierarchy_dict)
        print(self.color_dict)

        self.set_axes()
        
    def set_axes(self):
        # set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        # set limits
        self.ax.set_xlim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_ylim3d([-self.MAX_DIM, self.MAX_DIM])
        self.ax.set_zlim3d([-self.MAX_DIM + self.Z_OFFSET, self.MAX_DIM + self.Z_OFFSET])

    def draw_hand(self, landmarks):
        # check if there's something to be drawn
        if len(landmarks) == 0:
            return
        landmarks = np.array(landmarks)
        # draw in each color
        for color, indexes in self.color_dict.items():
            cur_vectors = landmarks[indexes]
            self.ax.plot(
                xs=cur_vectors[:, 0],
                ys=cur_vectors[:, 1],
                zs=cur_vectors[:, 2],
                color=color,
                marker='o'
                )

        

     
    def update_points(self, joint_coordinates, pause = 0.01, cameras=None, camera_colors=None):
        """
        Takes and array of 3d vectors with point coordinates.
        Updates plot.
        """

        # clear previous drawings
        self.ax.cla()

        # draw the hand
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