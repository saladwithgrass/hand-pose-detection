import cv2
import numpy as np
import argparse
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cam_id', help='device id for camera that will be calibrated', type=int)
    args = parser.parse_args()
    cam_id = args.cam_id

    # board parameters
    CHARUCO_BOARD_ROWS = 8
    CHARUCO_BOARD_COLS = 11
    CHARUCO_SQUARE_SIZE = 23  # mm
    CHARUCO_MARKER_SIZE = 17
    ARUCO_DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)


    # create board
    charuco_board = cv2.aruco.CharucoBoard(
        size=(CHARUCO_BOARD_COLS, CHARUCO_BOARD_ROWS),
        squareLength=CHARUCO_SQUARE_SIZE,
        markerLength=CHARUCO_MARKER_SIZE,
        dictionary=ARUCO_DICTIONARY
    )

    # create detector
    detector = cv2.aruco.CharucoDetector(
        board=charuco_board
    )

    # points for calibration
    all_image_points = []
    all_object_points = []

    # calibration frame counter
    calibration_counter = 0

    # open camera by id
    cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    image_size = None

    # read indefinitely
    while True:
        # get frame
        ret, image = cap.read()
        
        # get image size
        image_size = image.shape[0:2][::-1]

        # chek if all is ok
        if not ret:
            break
        
        # conver colors for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect board with detector
        charuco_corners, \
        charuco_ids, \
        marker_corners, \
        marker_ids = detector.detectBoard(
            image=gray,
            charucoCorners=None, 
            charucoIds=None
        )

        # if corners detected, draw them
        if charuco_corners is not None and charuco_ids is not None:
            cv2.aruco.drawDetectedCornersCharuco(
                image=image, 
                charucoCorners=charuco_corners,
                charucoIds=charuco_ids,
                cornerColor=(255, 0, 255)
                ) 
            
        # display result
        cv2.imshow('huh', image)
            
        # wait and get key
        key = cv2.waitKey(1)
            
        # if key is esc, then break
        if key == 27:
            break

        # if told to capture a frame, capture it
        if charuco_corners is not None and len(charuco_corners) > 5:
            cur_object_points, cur_image_points = charuco_board.matchImagePoints(charuco_corners, charuco_ids)
            if len(cur_object_points) == 0 or len(cur_image_points) == 0:
                print('matching points failed. you should retry')
                continue

            calibration_counter += 1
            print(f'frame added. total frames: {calibration_counter}')
            all_image_points.append(cur_image_points)
            all_object_points.append(cur_object_points)
            
    
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

    data_dict = {
        'camera_matrix' : camera_matrix,
        'dist_coeffs' : dist_coeffs
    }
    with open(f'calibration_{cam_id}.pkl', 'wb') as output:
        pickle.dump(data_dict, output)

    # Release camera and close window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()