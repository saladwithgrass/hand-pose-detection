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

# to be removed later !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from utils.file_utils import create_charuco_from_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_ids', help='Device id of camera to capture.', type=int, nargs=2)
    parser.add_argument('-cj', '--capture_json', help='Path to json with capture parameters', default='../config/capture_params.json')
    parser.add_argument('-ci', '--camera-intrinsics', help='Path to .pkl file with camera intrinsic parameters.', required=True, nargs=2)

    args = parser.parse_args()
    cam_ids = args.cam_ids

    # create capture
    caps = []
    for cam_id in cam_ids:
        caps.append(create_capture_from_json(cam_id, args.capture_json))
    
    # import camera intrinsics
    cam_matrices = []
    dist_coeffs = []
    new_cam_matrices = []
    rois = []
    for intr_filename in args.camera_intrinsics:
        with open(intr_filename, 'rb') as intr_file:
            intr_dict = pickle.load(intr_file)
            cam_matrices.append(intr_dict['camera_matrix'])
            dist_coeffs.append(intr_dict['dist_coeffs'])

    # create visualizer
    visualizer = Visualizer3D()

    # create charuco detector
    detector = aruco.ArucoDetector(
        dictionary=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    )
    marker_length = 50.
    objPoints = np.zeros((4,3))
    objPoints[0] = [-marker_length/2., marker_length/2.,  0]
    objPoints[1] = [marker_length/2., marker_length/2.,   0]
    objPoints[2] = [marker_length/2., -marker_length/2.,  0]
    objPoints[3] = [-marker_length/2., -marker_length/2., 0]


    # read frame by frame
    while True:
        ret, frame = cap.read()

        # check if read succeeded
        if not ret:
            break

        # -------------------- Position detection part begin ------------------

        # convert colors
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect aruco 
        aruco_corners, aruco_ids, _ = detector.detectMarkers(frame)
        aruco_corners = np.array(aruco_corners)
        if len(aruco_corners) != 0:
            cv2.polylines(frame, aruco_corners[0].astype(np.int32), isClosed=True, color=(255, 0, 255), thickness=3)
            # estimate aruco pose
            ret, rvec, tvec = cv2.solvePnP(
                objectPoints=objPoints,
                imagePoints=aruco_corners[0],
                cameraMatrix=camera_matrix, 
                distCoeffs=dist_coeffs);
            if ret:
                # draw axes
                cv2.drawFrameAxes(
                    frame, 
                    cameraMatrix=camera_matrix,
                    distCoeffs=dist_coeffs,
                    rvec=rvec,
                    tvec=tvec,
                    length=200,
                    thickness=10
                    )
                visualizer.update_points([tvec])

        # -------------------- Position detection part end -------------------- 

        # update visualizer
        scale = 0.4
        cv2.imshow('huh', cv2.resize(frame, dsize=None, fx=scale, fy=scale))
        # wait and lsiten for exit
        if cv2.waitKey(1) == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()