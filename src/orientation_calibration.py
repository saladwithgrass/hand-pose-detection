import cv2
import pickle 
import argparse
import cv2.aruco as aruco
import numpy as np

from utils.file_utils import (
    create_capture_from_json, 
<<<<<<< HEAD:src/orientation_calibration.py
    create_charuco_from_json,
    load_intr_with_minimal_error
    )

from utils.draw_utils import draw_text
>>>>>>> 711a6f1 (reorganized files and started work on gripper conversion hierarchy):calibration/orientation_calibration.py

def click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Clicked on (x, y): ({x}, {y})')

# SECTION SAVE_FUNC BEGIN
def save(input_sources, rvecs, tvecs, extrinsics, separate, output):
    print('Saving data for cameras', end='')
    if separate:
        print(' separately.')
        prefix = output
        prefix.removesuffix('.pkl')
        for idx in range(len(input_sources)):
            cur_name = prefix + f'_{input_sources[idx]}.pkl'
            data_struct = {
                'rvec' : rvecs[idx],
                'tvec' : tvecs[idx],
                'extrinsics' : extrinsics[idx],
                'cam_id' : input_sources[idx]
            }
            with open(cur_name, 'wb') as output:
                pickle.dump(data_struct, output)
            print(f'Saved as {cur_name}.')
    else:
        print(' in one file.')
        data_struct = {
            'rvecs' : rvecs,
            'tvecs' : tvecs,
            'extrinsics' : extrinsics,
            'cam_ids' : input_sources
        }
        output_name = output
        output_name.removesuffix('pkl')
        output_name = output_name + '.pkl'
        with open(output_name, 'wb') as output:
            pickle.dump(data_struct, output)
        print(f'Saved to {output_name}')
# SECTION SAVE_FUNC END

# SECTION INPUT_SOURCES BEGIN
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_sources', 
        help='camera device id /dev/vid* or path to video', 
        nargs='+', 
        )
# SECTION INPUT_SOURCES END

# SECTION INTRINSICS_FILES BEGIN
    parser.add_argument(
        '-if', '--intrinsics-files', 
        help='path to .pkl file with data from intrinsics calibration.' +
            'Must correspond to cam_ids', 
        nargs='+',
        required=False
        )
# SECTION INTRINSICS_FILES END

# SECTION OUTNAME BEGIN
    parser.add_argument(
        '-o', '--output', 
        help='Path to output file.', 
        type=str, 
        default='../calibration_data/orientation'
    )
# SECTION OUTNAME END

# SECTION SEPARATE BEGIN
    parser.add_argument(
        '-s', '--separate', 
        help='If set, stores cameras orientations in separate files.', 
        action='store_true'
    )
# SECTION SEPARATE END

# SECTION DISPLAY_SCALE BEGIN
    parser.add_argument(
        '-ds', '--display-scale', 
        help='Sets display scaling for images', 
        type=float, 
        default=0.4
    )
# SECTION DISPLAY_SCALE END

# SECTION INIT BEGIN
    args = parser.parse_args()

    # set some args as variables
    input_sources = args.input_sources
    scale = args.display_scale

    cv2.setNumThreads(16)
    if len(input_sources) != len(args.intrinsics_files):
        print('Amount of inputs and intrinsics file must match. Aborting')
        return
# SECTION INIT END

# SECTION PREP_CAMS BEGIN
    # check if everything is camera:
    use_camera_input = True 
    for input_source in input_sources:
        use_camera_input = use_camera_input and input_source.isdigit()

    # empty list for captures
    caps = list()
    # open cameras if we use them
    if use_camera_input:
        cam_ids = input_sources

        # open camera captures
        for cam_id in cam_ids:
            caps.append(create_capture_from_json(int(cam_id), '../config/capture_params.json'))
    else:
        for input_source in input_sources:
            caps.append(cv2.VideoCapture(input_source))
# SECTION PREP_CAMS END

# SECTION LOAD_INTR BEGIN
    cam_matrices = list()
    dist_coeffs = list()
    intrinsics_files = args.intrinsics_files

    # load intrinsics
    for intr_file in intrinsics_files:
        with open(intr_file, 'rb') as intr_input:
            cam_intrinsics = pickle.load(intr_input)
            cam_matrices.append(cam_intrinsics['camera_matrix'])
            dist_coeffs.append(cam_intrinsics['dist_coeffs'])
# SECTION LOAD_INTR END

# SECTION CHARUCO_SETUP BEGIN
    # create charuco board from default parameters
    charuco_board = create_charuco_from_json()

    # create charuco detector
    detector = aruco.CharucoDetector(charuco_board)
# SECTION CHARUCO_SETUP END
    
# SECTION READ_INIT BEGIN
    # read frame by frame
    captured_frames = [None] * len(caps)
    all_ok:bool = True
    cam_rvecs = [None] * len(caps)
    cam_tvecs = [None] * len(caps)
    cam_extrinsics = [None] * len(caps)

    # honestly, i do not even remember why this is here,
    # maybe it should be here, maybe it should not.
    # i'll leave it for now
    for _ in range(100):
        for cap in caps:
            cap.read()

# SECTION READ_INIT END

# SECTION READ_FRAME BEGIN
    while all_ok:
        idx = 0
        for cap in caps:
            ret, frame = cap.read()
            # chek if read succeeded
            if not ret:
                all_ok = False
                break
# SECTION READ_FRAME END

# SECTION DISCOLOR BEGIN
            # convert colors
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# SECTION DISCOLOR END

# SECTION DETECT BEGIN
            # detect board
            charuco_corners, \
            charuco_ids, \
            marker_corners, \
            marker_ids = detector.detectBoard(
                image=gray
            )
# SECTION DETECT END

# SECTION POSE_ESTIM BEGIN
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
# SECTION POSE_ESTIM END

# SECTION POSE_DISPLAY BEGIN
            if ret:
                # x - red
                # y - green
                # z - blue

                # save orientation
                cam_rvecs[idx] = rvec
                cam_tvecs[idx] = [tvec]
                cv2.drawFrameAxes(
                    image=frame,
                    cameraMatrix=cam_matrices[idx],
                    distCoeffs=dist_coeffs[idx],
                    rvec=rvec,
                    tvec=tvec,
                    length=100,
                    thickness=10
                )
            cur_window_name = f'source:{input_sources[idx]}'
            draw_text(frame, cur_window_name)
            cv2.imshow(cur_window_name, cv2.resize(frame, dsize=(None), fx=scale, fy=scale))
            cv2.setMouseCallback(cur_window_name, click_callback)
            idx += 1
# SECTION POSE_DISPLAY END

# SECTION CMD_INPUT BEGIN
        # i have no idea why i set timeout on waitKey to 5
        # maybe there was some reason?
        key = cv2.waitKey(5)
        if key == 27:
            break
        elif key == ord('a'):
            pass
        elif key == ord('c'):
            save(
                input_sources=input_sources,
                rvecs=cam_rvecs,
                tvecs=cam_tvecs,
                extrinsics=cam_extrinsics,
                separate=args.separate,
                output=args.output
            )
            return
# SECTION CMD_INPUT END


if __name__ == '__main__':
    main()
