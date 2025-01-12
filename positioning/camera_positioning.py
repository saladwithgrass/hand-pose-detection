import numpy as np
import argparse
import pickle
import cv2

import sys
sys.path.append('../')
from utils.visualizer_3d import Visualizer3D

def get_camera_coordinates(u:float, v:float):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-co', '--cameras-orientation', \
                        help='.pkl file(s) with cameras orientation. Can accept separate files.', \
                        nargs='+', \
                        required=True
                        )
    args = parser.parse_args()
    
    # laod camera orientations
    camera_files = args.cameras_orientation
    cam_rvecs = []
    cam_tvecs = []
    # if there's a single file, parse it
    if len(camera_files) == 1:
        camera_files = camera_files[0]
        with open(camera_files, 'rb') as input_file:
            cam_dict = pickle.load(input_file)
            cam_rvecs = cam_dict['rvecs']
            cam_tvecs = cam_dict['tvecs']
    else: # if there are multiple, parse them
        for camera_file in camera_files:
            with open(camera_file, 'rb') as input_file:
                cam_dict = pickle.load(input_file)
                cam_rvecs.append(cam_dict['rvec'])
                cam_tvecs.append(cam_dict['tvec'])

    # create visualizer
    visualizer = Visualizer3D()

    # to get cameras orientation relative to charuco board, i have to inverse transforms
    inv_tvecs = []
    for tvec, rvec in zip(cam_tvecs, cam_rvecs):
        new_rvec = cv2.Rodrigues(rvec)[0]
        print(new_rvec.shape)
        homo_matrix = np.hstack((new_rvec, tvec))
        homo_matrix = np.vstack((homo_matrix, [0, 0, 0, 1]))
        homo_matrix = np.linalg.inv(homo_matrix)
        homo_matrix = homo_matrix.reshape(4, 4)
        print(homo_matrix[0:3, 3])
        inv_tvecs.append(homo_matrix[0:3, 3])

    # inv_tvecs.append(np.zeros(shape=(3,1)))
    print(inv_tvecs)
    visualizer.update_points(inv_tvecs, pause=1000)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()