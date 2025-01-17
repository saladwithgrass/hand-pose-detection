import cv2
import cv2.aruco as aruco
import matplotlib.pyplot as plt
import argparse
import pickle
import numpy as np

import sys
sys.path.append('../')
from utils.visualizer_3d import Visualizer3D 
from utils.file_utils import create_capture_from_json
from triangulator import create_triangulator_from_files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_ids', help='Device id of camera to capture.', type=int, nargs=2)
    parser.add_argument('-cj', '--capture_json', help='Path to json with capture parameters', default='../config/capture_params.json')
    parser.add_argument('-ci', '--camera-intrinsics', help='Path to .pkl file with camera intrinsic parameters.', required=True, nargs=2)
    parser.add_argument('-or', '--orientation', help='Path to .pkl file with camera position parameters.', required=True, nargs=2)
    parser.add_argument('-nt', '--num-threads', type=int, default=8)
    parser.add_argument('-nv', '--no-video', help='If set, will not display images from cameras.', action='store_true')

    args = parser.parse_args()
    
    # set arguments
    cv2.setNumThreads(args.num_threads)
    cam_ids = args.cam_ids
    no_video = args.no_video    

    # ----------------------------------- setup -----------------------------------

    # create captures
    caps = []
    for cam_id in cam_ids:
        caps.append(create_capture_from_json(cam_id, args.capture_json))
    
    
    # create triangulator
    triangulator = create_triangulator_from_files(
        intr_files=args.camera_intrinsics,
        orientation_files=args.orientation
        )

    # create visualizer
    visualizer = Visualizer3D()

    # create aruco detector
    detector = aruco.ArucoDetector(
        dictionary=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    )
    marker_length = 50.
    objPoints = np.zeros((4,3))
    objPoints[0] = [-marker_length/2., marker_length/2.,  0]
    objPoints[1] = [marker_length/2., marker_length/2.,   0]
    objPoints[2] = [marker_length/2., -marker_length/2.,  0]
    objPoints[3] = [-marker_length/2., -marker_length/2., 0]

    frames = [None, None]
    camera_points = [None, None]

    # ----------------------------------- running -----------------------------------

    # read frame by frame
    while True:
        # zero points out
        camera_points = [None, None] 

        # read frames from caps
        for idx in range(len(caps)):
            ret, frames[idx] = caps[idx].read()

            # check if read succeeded
            if not ret:
                break

        # -------------------- Position detection part begin ------------------
        idx = 0
        for frame in frames:
            # convert colors
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect aruco 
            aruco_corners, aruco_ids, _ = detector.detectMarkers(frame)
            aruco_corners = np.array(aruco_corners)
            # check if detection happened
            if aruco_ids is not None and 0 in aruco_ids:
                # add aruco corners to points that will be triangulated
                for aruco_idx in range(len(aruco_ids)):
                    if aruco_ids[aruco_idx] == 0:
                        camera_points[idx] = np.reshape(aruco_corners[aruco_idx], (4, 2))
                        cv2.polylines(frame, aruco_corners[0].astype(np.int32), isClosed=True, color=(255, 0, 255), thickness=3)
                        break

            idx += 1
        # -------------------- Position detection part end -------------------- 

        # make sure that marker is visible on both cameras
        if camera_points[0] is None or camera_points[1] is None:
            print('One camera did not detect markers. Skipping.')
            continue

        # triangulate each corner
        points3d = []
        for point1, point2 in zip(camera_points[0], camera_points[1]):
            points3d.append(triangulator.triangulate([point1, point2]))
            print(points3d[-1])

        # update visualizer
        print('updating visualiser')
        visualizer.update_points(points3d)

        scale = 0.4
        idx = 0
        if not no_video:
            for frame in frames:
                cv2.imshow(f'huh{idx}', cv2.resize(frame, dsize=None, fx=scale, fy=scale))
                idx += 1
        # wait and lsiten for exit
        if cv2.waitKey(1) == 27:
            break
    
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()