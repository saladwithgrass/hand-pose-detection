import cv2
import numpy as np
import argparse
import pickle

import sys
sys.path.append('../')
from utils.file_utils import (
    create_capture_from_json,
    create_charuco_from_json
)

def main():
# SECTION CAMID BEGIN 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cam_id', 
        help='device id for camera that will be calibrated', 
        type=int
        )
# SECTION CAMID END

# SECTION NAMEARGS BEGIN
    parser.add_argument(
        '-ne',
        '--no-error-name',
        help='Prevents error from being added to the name of ouput.',
        action='store_true'
    )
    parser.add_argument(
        '-nf',
        '--no-frames-name',
        help='Prevents number of frames from being added to the name of output',
        action='store_true'
    )
# SECTION NAMEARGS END

# SECTION OUTPUTNAME BEGIN
    parser.add_argument(
        '-o',
        '--output',
        help='Path to output file',
        default = None
    )
# SECTION OUTPUTNAME END

# SECTION CAPTUREJSON BEGIN
    parser.add_argument(
        '-cj',
        '--capture_json',
        help='Path to json with capture parameters',
        default='../config/capture_params.json'
    )
# SECTION CAPTUREJSON END

# SECTION NUMTHREADS BEGIN
    parser.add_argument(
        '-nt',
        '--num-threads',
        help='Number of threads used in cv2.setNumThreads.',
        type=int
    )
# SECTION NUMTHREADS END

# SECTION PARSE BEGIN
    args = parser.parse_args()
    cam_id = args.cam_id
# SECTION PARSE END

# SECTION CREATECHARUCO BEGIN
    # create charuco from default parameters
    charuco_board = create_charuco_from_json()

    # create detector
    detector = cv2.aruco.CharucoDetector(
        board=charuco_board
    )
# SECTION CREATECHARUCO END

# SECTION BASICINIT BEGIN
    # points for calibration
    all_image_points = []
    all_object_points = []

    # calibration frame counter
    calibration_counter = 0
    
    image_size = None
# SECTION BASICINIT END

# SECTION CREATECAPTURE BEGIN
    # open camera by id
    cap = create_capture_from_json(cam_id, args.capture_json)
# SECTION CREATECAPTURE END

# SECTION READFRAME BEGIN
    # read indefinitely
    while True:
        # get frame
        ret, image = cap.read()

        # chek if all is ok
        if not ret:
            break
# SECTION READFRAME END
        
# SECTION GETSIZE BEGIN
        # get image size
        image_size = image.shape[0:2][::-1]
# SECTION GETSIZE END

# SECTION DISCOLOR BEGIN
        # conver colors for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# SECTION DISCOLOR END

# SECTION DETECT BEGIN
        # detect board with detector
        charuco_corners, \
        charuco_ids, \
        marker_corners, \
        marker_ids = detector.detectBoard(
            image=gray,
            charucoCorners=None, 
            charucoIds=None
        )
        if charuco_corners is None:
            continue
# SECTION DETECT END

# SECTION DISPLAY BEGIN
        # if corners detected, draw them
        if charuco_ids is not None:
            cv2.aruco.drawDetectedCornersCharuco(
                image=image, 
                charucoCorners=charuco_corners,
                charucoIds=charuco_ids,
                cornerColor=(255, 0, 255)
                ) 
            
        # display result
        cv2.imshow('huh', cv2.resize(image, dsize=None, fx=0.3, fy=0.3))
# SECTION DISPLAY END

# SECTION SAVEPOINTS BEGIN
        enough_corners_detected = len(charuco_corners) > 11
        if enough_corners_detected:
            (cur_object_points, 
            cur_image_points) = charuco_board.matchImagePoints(
                charuco_corners, 
                charuco_ids
            )
            if len(cur_object_points) == 0 or len(cur_image_points) == 0:
                print('matching points failed. you should retry')
                continue
            
            calibration_counter += 1
            print(f'frame added. total frames: {calibration_counter}')
            all_image_points.append(cur_image_points)
            all_object_points.append(cur_object_points)
# SECTION SAVEPOINTS END

# SECTION WAITKEY BEGIN
        # wait and get key
        key = cv2.waitKey(1)
            
        # if key is esc, then break
        if key == 27:
            break
# SECTION WAITKEY END
            
# SECTION CV2CLOSE BEGIN
    # release camera and close window
    cap.release()
    cv2.destroyAllWindows()
# SECTION CV2CLOSE END

# SECTION CALIBRATION BEGIN
    # calibrate camera with collected data
    print('starting calibration...', flush=True)
    precision, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
        objectPoints=all_object_points, 
        imagePoints=all_image_points, 
        imageSize=image_size,
        cameraMatrix=None,
        distCoeffs=None
        )
    print(f'camera calibrated with error of {precision}')
# SECTION CALIBRATION END

# SECTION SAVEDATA BEGIN
    data_dict = {
        'camera_matrix' : camera_matrix,
        'dist_coeffs' : dist_coeffs,
        'image_size' : image_size
    }

    file_name = args.output
    if file_name is None:
        file_name = f'calibration_{cam_id}'
    
    if not args.no_frames_name:
        file_name = file_name + f'_frames={calibration_counter}'
    
    if not args.no_error_name:
        file_name = file_name + f'_error={precision}'

    with open(f'{file_name}.pkl', 'wb') as output:
        pickle.dump(data_dict, output)
# SECTION SAVEDATA END


if __name__ == '__main__':
    main()
