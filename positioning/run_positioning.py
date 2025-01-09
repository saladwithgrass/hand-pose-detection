import cv2
import cv2.aruco as aruco
import matplotlib.pyplot as plt
import argparse
import pickle

import sys
sys.path.append('../')
from utils.visualizer_3d import Visualizer3D 
from utils.capture_opener import create_capture_from_json

# to be removed later !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from utils.calibration_utils import create_charuco_from_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_id', help='Device id of camera to capture.', type=int)
    parser.add_argument('-cj', '--capture_json', help='Path to json with capture parameters', default='../config/capture_params.json')
    parser.add_argument('-ci', '--camera-intrinsics', help='Path to .pkl file with camera intrinsic parameters.', required=True)

    args = parser.parse_args()
    cam_id = args.cam_id

    # create capture
    cap = create_capture_from_json(cam_id, args.capture_json)
    
    # create visualizer
    visualizer = Visualizer3D()

    # create charuco board from default parameters
    charuco_board = create_charuco_from_json('../calibration/charuco_parameters.json')

    # create charuco detector
    detector = aruco.CharucoDetector(charuco_board)

    # import camera intrinsics
    with open(args.camera_intrinsics, 'rb') as intr_file:
        intr_dict = pickle.load(intr_file)
        camera_matrix = intr_dict['camera_matrix']
        dist_coeffs = intr_dict['dist_coeffs']

    # read frame by frame
    while True:
        ret, frame = cap.read()

        # check if read succeeded
        if not ret:
            break

        xs = []
        ys = []
        zs = []
        # -------------------- Position detection part begin ------------------

        # convert colors
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect board
        charuco_corners, \
        charuco_ids, \
        marker_corners, \
        marker_ids = detector.detectBoard(
            image=gray
        )

        # estimate pose
        char_ret, rvec, tvec = \
            aruco.estimatePoseCharucoBoard(
            charucoCorners=charuco_corners,
            charucoIds=charuco_ids,
            cameraMatrix=camera_matrix,
            distCoeffs=dist_coeffs,
            board=charuco_board,
            rvec=None,
            tvec=None
        )

        # check if estimation worked
        if not char_ret:
            continue

        # set xs, ys and zs
        xs = [tvec[0]]
        ys = [tvec[1]]
        zs = [tvec[2]]

        # -------------------- Position detection part end -------------------- 

        # update visualizer
        visualizer.update_points([tvec, tvec, tvec])

        # wait and lsiten for exit
        if cv2.waitKey(10) == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()