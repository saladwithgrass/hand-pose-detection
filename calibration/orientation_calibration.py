import cv2
import pickle 
import argparse
import cv2.aruco as aruco

import sys
sys.path.append('../')
from utils.capture_opener import create_capture_from_json
from utils.calibration_utils import create_charuco_from_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_id', help='camera device id /dev/vid*', type=int)
    parser.add_argument('intrinsics_file', help='path to .pkl file with data from intrinsics calibration')
    args = parser.parse_args()

    # create charuco board from default parameters
    charuco_board = create_charuco_from_json()

    # create charuco detector
    detector = aruco.CharucoDetector(charuco_board)

    # load intrinsics
    intrinsics_file = args.intrinsics_file
    with open(intrinsics_file, 'rb') as intr_input:
        cam_intrinsics = pickle.load(intr_input)
        camera_matrix = cam_intrinsics['camera_matrix']
        dist_coeffs = cam_intrinsics['dist_coeffs']

    # open camera capture
    cam_id = args.cam_id
    cap = create_capture_from_json(cam_id, '../config/capture_params.json')
    
    # read frame by frame
    while True:
        ret, frame = cap.read()

        # chek if read succeeded
        if not ret:
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
            cameraMatrix=camera_matrix,
            distCoeffs=dist_coeffs,
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
                cameraMatrix=camera_matrix,
                distCoeffs=dist_coeffs,
                rvec=rvec,
                tvec=tvec,
                length=100,
                thickness=10
            )

        scale = 0.4
        cv2.imshow('huh', cv2.resize(frame, dsize=(None), fx=scale, fy=scale))
        cv2.waitKey(10)


if __name__ == '__main__':
    main()