import cv2
import cv2.aruco as aruco
import matplotlib.pyplot as plt
import argparse
import pickle
import numpy as np
from time import time

from utils.visualizer_3d import Visualizer3D 
from utils.file_utils import create_capture_from_json
from positioning.triangulator import create_triangulator_from_files
from detection.capture_detector import CaptureDetector
from utils.draw_utils import draw_hand_on_image
from gripper_conversion.gripper_converter import GripperConverter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_ids', help='Device id of camera to capture.', type=int, nargs=2)
    parser.add_argument('-cj', '--capture_json', help='Path to json with capture parameters', default='../config/capture_params.json')
    parser.add_argument('-ci', '--camera-intrinsics', help='Path to .pkl file with camera intrinsic parameters.', required=True, nargs=2)
    parser.add_argument('-or', '--orientation', help='Path to .pkl file with camera position parameters.', required=True, nargs=2)
    parser.add_argument('-nt', '--num-threads', type=int, default=8)
    parser.add_argument('-sc', '--show-video', help='If set, will display images from cameras.', action='store_true')
    parser.add_argument('-ds', '--display-scale', help='Scale of images from camera if they will be displayed.', type=float)
    parser.add_argument('-sh', '--show-hands', help='If set, will also display 3d representation of detected hands.', action='store_true')

    args = parser.parse_args()
    
    # set arguments
    cv2.setNumThreads(args.num_threads)
    cam_ids = args.cam_ids
    show_video = args.show_video    
    scale = args.display_scale
    show_hands = args.show_hands

    # ----------------------------------- setup -----------------------------------

    # create captures
    caps = []
    for cam_id in cam_ids:
        caps.append(create_capture_from_json(cam_id, args.capture_json))

    # create detectors for each capture
    detectors:list[CaptureDetector] = []
    for cap in caps:
        detectors.append(CaptureDetector(cap, '../detection/hand_landmarker.task')) 
    
    # create triangulator
    triangulator = create_triangulator_from_files(
        intr_files=args.camera_intrinsics,
        orientation_files=args.orientation
        )

    # create visualizer
    visualizer = Visualizer3D()

    # create converter to gripper
    gripper_converter = GripperConverter('../config/hand_connections.json')
    gripper_converter.set_orientation_index_z()

    frames = [None, None]
    camera_points = [None, None]

    # ----------------------------------- running -----------------------------------

    # read frame by frame
    while True:
        start_time = time()
        # zero points out
        camera_points = [None, None] 

        # read frames from caps
        for idx in range(len(detectors)):
            camera_points[idx], frames[idx] = detectors[idx].process_one_frame()

        # make sure that marker is visible on both cameras
        if camera_points[0] is None or camera_points[1] is None:
            print('One camera did not detect markers. Skipping.')
            visualizer.update_points([[0, 0, 0]])
            continue

        # triangulate each corner
        points3d = []
        for point1, point2 in zip(camera_points[0], camera_points[1]):
            points3d.append(triangulator.triangulate([point1, point2]))

        axes = None
        axes_center = None
        if len(points3d) != 0:
            # run gripper conversion
            axes, axes_center = gripper_converter.get_orientation_index_z(points3d=points3d)

        if not show_hands:
            points3d = None

        # update visualizer
        visualizer.update_points(joint_coordinates=points3d, axes=axes, axes_center=axes_center)

        # display frames from camera if needed
        if show_video:
            # process each frame from cameras
            for cam_idx in range(len(frames)):
                # draw hand
                draw_hand_on_image(
                    frames[cam_idx], 
                    camera_points[cam_idx], 
                    color_dict=visualizer.color_dict, 
                    hierarchy_dict=visualizer.hierarchy_dict
                    )
                # scale image and display it 
                cv2.imshow(f'huh{idx}', cv2.resize(frames[cam_idx], dsize=None, fx=scale, fy=scale))

        end_time = time()
        print('FPS: ', 1/ (end_time - start_time))
        # wait and lsiten for exit
        if cv2.waitKey(1) == 27:
            break
    
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
