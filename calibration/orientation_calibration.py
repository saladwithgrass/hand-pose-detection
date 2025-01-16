import cv2
import pickle 
import argparse
import cv2.aruco as aruco
import numpy as np

import sys
sys.path.append('../')
from utils.file_utils import (
    create_capture_from_json, 
    create_charuco_from_json
    )

def click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Clicked on (x, y): ({x}, {y})')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_ids', 
                        help='camera device id /dev/vid*', 
                        nargs='+', 
                        type=int)

    parser.add_argument('-if', '--intrinsics_files', 
                        help='path to .pkl file with data from intrinsics calibration. Must correspond to cam_ids', 
                        nargs='+',
                        required=True
                        )
    parser.add_argument('-o', '--output', help='Path to output file.', type=str, default='orientation')
    parser.add_argument('-s', '--separate', help='If set, stores cameras orientations in separate files.', action='store_true')
    parser.add_argument('-ds', '--display-scale', help='How shows how much images from cameras will be scaled down when displayed.', type=float, default=0.4)
    args = parser.parse_args()

    scale = args.display_scale

    if len(args.cam_ids) != len(args.intrinsics_files):
        print('Amount of input devices and intrinsics file must match. Aborting')
        return
    
    cam_ids = args.cam_ids
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
    for cam_id in cam_ids:
        caps.append(create_capture_from_json(cam_id, '../config/capture_params.json'))
    
    # read frame by frame
    captured_frames = [None] * len(caps)
    all_ok:bool = True
    cam_rvecs = [None] * len(caps)
    cam_tvecs = [None] * len(caps)
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
                cam_rvecs[idx] = rvec
                cam_tvecs[idx] = tvec
                cv2.drawFrameAxes(
                    image=frame,
                    cameraMatrix=cam_matrices[idx],
                    distCoeffs=dist_coeffs[idx],
                    rvec=rvec,
                    tvec=tvec,
                    length=100,
                    thickness=10
                )
            cur_window_name = f'camera:{cam_ids[idx]}'
            cv2.imshow(cur_window_name, cv2.resize(frame, dsize=(None), fx=scale, fy=scale))
            cv2.setMouseCallback(cur_window_name, click_callback)
            idx += 1
        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key == ord('a'):
            pass
        elif key == ord('c'):
            print('Saving data for cameras', end='')
            if args.separate:
                print(' separately.')
                prefix = args.output
                prefix.removesuffix('.pkl')
                for idx in range(len(cam_ids)):
                    cur_name = prefix + f'_{cam_ids[idx]}.pkl'
                    data_struct = {
                        'rvec' : cam_rvecs[idx],
                        'tvec' : cam_tvecs[idx],
                        'cam_id' : cam_ids[idx]
                    }
                    with open(cur_name, 'wb') as output:
                        pickle.dump(data_struct, output)
                    print(f'Saved as {cur_name}.')
            else:
                print(' in one file.')
                data_struct = {
                    'rvecs' : cam_rvecs,
                    'tvecs' : cam_tvecs,
                    'cam_ids' : cam_ids
                }
                output_name = args.output
                output_name.removesuffix('pkl')
                output_name = output_name + '.pkl'
                with open(output_name, 'wb') as output:
                    pickle.dump(data_struct, output)
                print(f'Saved to {output_name}')
            return
                        


if __name__ == '__main__':
    main()