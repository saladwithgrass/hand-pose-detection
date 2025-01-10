import cv2
import pickle 
import argparse
import cv2.aruco as aruco
import numpy as np

import sys
sys.path.append('../')
from utils.capture_opener import create_capture_from_json
from utils.calibration_utils import create_charuco_from_json



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_ids', 
                        help='camera device id /dev/vid*', 
                        nargs='+', 
                        type=int)

    parser.add_argument('intrinsics_files', 
                        help='path to .pkl file with data from intrinsics calibration. Must correspond to cam_ids', 
                        nargs='+'
                        )
    args = parser.parse_args()

    # create charuco board from default parameters
    charuco_board = create_charuco_from_json()

    # create charuco detector
    detector = aruco.CharucoDetector(charuco_board)

    # load intrinsics
    intrinsics_files = args.intrinsics_files
    cam_matrices = list()
    dist_coeffs = list()
    for intr_file in intrinsics_files:
        with open(intr_file, 'rb') as intr_input:
            cam_intrinsics = pickle.load(intr_input)
            cam_matrices.append(cam_intrinsics['camera_matrix'])
            dist_coeffs.append(cam_intrinsics['dist_coeffs'])

    # open camera capture
    caps = list()
    for cam_id in args.cam_ids:
        caps.append(create_capture_from_json(cam_id, '../config/capture_params.json'))
    
    # read frame by frame
    captured_frames = [None] * len(caps)
    all_ok:bool = True
    while all_ok:
        idx = 0
        for cap in caps:
            ret, frame = cap.read()
            # chek if read succeeded
            if not ret:
                all_ok = False
                break

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
            ret, rvec, tvec = \
                aruco.estimatePoseCharucoBoard(
                charucoCorners=charuco_corners,
                charucoIds=charuco_ids,
                cameraMatrix=cam_matrices[idx],
                distCoeffs=dist_coeffs[idx],
                board=charuco_board,
                rvec=None,
                tvec=None
            )
            if ret:
                # x - red
                # y - green
                # z - blue
                cv2.drawFrameAxes(
                    image=frame,
                    cameraMatrix=cam_matrices[idx],
                    distCoeffs=dist_coeffs[idx],
                    rvec=rvec,
                    tvec=tvec,
                    length=100,
                    thickness=10
                )

            scale = 0.3
            cv2.imshow('huh', cv2.resize(frame, dsize=(None), fx=scale, fy=scale))
            idx += 1
        cv2.waitKey(1)


if __name__ == '__main__':
    main()