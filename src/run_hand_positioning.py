from os import error
import cv2
import argparse
from time import time
import numpy as np

from utils.visualizer_3d import Visualizer3D 
from utils.file_utils import create_capture_from_json
from positioning.triangulator import create_triangulator_from_files
from detection.capture_detector import CaptureDetector
from utils.draw_utils import draw_hand_on_image, visualize_basic_gripper
# from gripper_conversion.test_gripper_converter import TestGripperConverter as GripperConverter
from gripper_conversion.basic_gripper_converter import BasicGripperConverter as GripperConverter


# SECTION CAM_IDS BEGIN
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cam_ids',
        help='Device id of camera to capture.',
        type=int,
        nargs=2
    )
# SECTION CAM_IDS END

# SECTION CAPTURE_JSON BEGIN
    parser.add_argument(
        '-cj',
        '--capture_json',
        help='Path to json with capture parameters',
        default='config/capture_params.json',
        required=False
    )
# SECTION CAPTURE_JSON END

# SECTION CAMERA_PARAMETERS BEGIN
    parser.add_argument(
        '-ci',
        '--camera-intrinsics',
        help='Path to .pkl file with camera intrinsic parameters.',
        required=True,
        nargs=2
    )
    parser.add_argument(
        '-or',
        '--orientation',
        help='Path to .pkl file with camera position parameters.',
        required=True,
        nargs=2
    )
# SECTION CAMERA_PARAMETERS END

# SECTION N_THREADS BEGIN
    parser.add_argument(
        '-nt',
        '--num-threads',
        type=int,
        default=8
    )
# SECTION N_THREADS END

# SECTION ARGS_VIDEO BEGIN
    parser.add_argument(
        '-sv',
        '--show-video',
        help='If set, will display images from cameras.',
        action='store_true'
    )
    parser.add_argument(
        '-ds',
        '--display-scale',
        help='Scale of images from camera if they will be displayed.',
        type=float,
        default=0.4
    )
# SECTION ARGS_VIDEO END

    parser.add_argument(
            '--distance',
            '-d',
            help='actaul distance between fingers',
            type=float
    )
# SECTION ARGS_HANDS BEGIN
    parser.add_argument(
        '-sh',
        '--show-hands',
        help='If set, will also display 3d representation of detected hands.',
        action='store_true'
    )

    args = parser.parse_args()
    return args
# SECTION ARGS_HANDS END


# SECTION SAVE_ARGS BEGIN
def main():
    args = parse_args()
    # set arguments
    cv2.setNumThreads(args.num_threads)
    cam_ids = args.cam_ids
    show_video = args.show_video    
    scale = args.display_scale
    show_hands = args.show_hands
# SECTION SAVE_ARGS END
    error_squared = 0.
    index_pos = 0
    n_measurements = 0
    actual_distance = args.distance

# SECTION DET_CAPS BEGIN
    # create captures
    caps = []
    for cam_id in cam_ids:
        caps.append(create_capture_from_json(cam_id, args.capture_json))

    # create detectors for each capture
    detectors:list[CaptureDetector] = []
    for cap in caps:
        detectors.append(CaptureDetector(cap, 'detection/hand_landmarker.task')) 
# SECTION DET_CAPS END

    distance = 0

# SECTION TRI_CREATE BEGIN
    # create triangulator
    triangulator = create_triangulator_from_files(
        intr_files=args.camera_intrinsics,
        orientation_files=args.orientation
        )
# SECTION TRI_CREATE END

# SECTION VIZ_CREATE BEGIN
    # create visualizer
    if show_hands:
        visualizer = Visualizer3D()
# SECTION VIZ_CREATE END

# SECTION GRIP_CONV BEGIN
    # create converter to gripper
    gripper_converter = GripperConverter('config/hand_connections.json')

# SECTION GRIP_CONV END

# SECTION INIT BEGIN
    frames = [[], []]
    camera_points = [[], []]

    # not important, for prettiness only
    new_rx = np.array([
            -1,  0,  0,
             0,  1,  0,
             0,  0, -1
        ]).reshape((3, 3))
    new_rvecs = np.copy(triangulator.rvecs)
    new_rvecs[0] = cv2.Rodrigues( cv2.Rodrigues(new_rvecs[0])[0] @ new_rx)[0]
    new_rvecs[1] = cv2.Rodrigues( cv2.Rodrigues(new_rvecs[1])[0] @ new_rx)[0]
# SECTION INIT END

# SECTION READ BEGIN
    # read frame by frame
    while True:
        start_time = time()
        # zero points out
        camera_points = [[], []] 

        # read frames from caps
        for idx in range(len(detectors)):
            camera_points[idx], frames[idx] = detectors[idx].process_one_frame()
# SECTION READ END

# SECTION BOTH_DETECTED BEGIN
        # make sure that marker is visible on both cameras
        if camera_points[0] is None or camera_points[1] is None:
            print('One camera did not detect markers. Skipping.')
            if show_hands:
                visualizer.update_points([[0, 0, 0]])
            continue
# SECTION BOTH_DETECTED END

# SECTION RUN_TRI BEGIN
        # triangulate each corner
        points3d = []
        for point1, point2 in zip(camera_points[0], camera_points[1]):
            points3d.append(triangulator.triangulate([point1, point2]))
        if len(points3d) > 8:
            index_pos = points3d[8]
# SECTION RUN_TRI END

# SECTION GET_ORIENT BEGIN
        axes = None
        axes_center = None
        if len(points3d) != 0:
            # run gripper conversion
            axes, axes_center, distance = gripper_converter.get_gripper_state(points3d=points3d)
# SECTION GET_ORIENT END

# SECTION UPDATE_VIZ BEGIN
        if show_hands:
            # update visualizer
            visualizer.update_points(joint_coordinates=points3d, axes=axes, axes_center=axes_center)
# SECTION UPDATE_VIZ END

# SECTION DISPLAY BEGIN
        # display frames from camera if needed
        if show_video:
            # process each frame from cameras
            for cam_idx in range(len(frames)):
                cv2.drawFrameAxes(
                    image=frames[cam_idx],
                    cameraMatrix=triangulator.camera_matrices[cam_idx],
                    distCoeffs=triangulator.dist_coeffs[cam_idx],
                    rvec=new_rvecs[cam_idx],
                    # rvec=triangulator.rvecs[cam_idx],
                    tvec=triangulator.tvecs[cam_idx],
                    length=100,
                    thickness=10
                )
                visualize_basic_gripper(frames[cam_idx], camera_points[cam_idx])
                # # draw hand
                # draw_hand_on_image(
                #     frames[cam_idx], 
                #     camera_points[cam_idx]
                #     )
                # scale image and display it 
                cv2.imshow(
                    f'huh{cam_idx}',
                    cv2.resize(frames[cam_idx],
                    dsize=None,
                    fx=scale,
                    fy=scale)
                )
# SECTION DISPLAY END

# SECTION TIME BEGIN
        end_time = time()
        print('FPS: ', 1/ (end_time - start_time), end=' ')
        print('Gripper Distance: ', distance)
        print('index pos: ', index_pos)
        # wait and lsiten for exit
        if cv2.waitKey(1) == 27:
            break
# SECTION TIME END
        if actual_distance is None:
            continue
        tolerance = 25.0 # mm
        error = distance - actual_distance
        if abs(error) < tolerance:
            error_squared += error*error
            n_measurements += 1
    
# SECTION FINISH BEGIN
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()
# SECTION FINISH END
    print('RMSE: ', np.sqrt(error_squared / n_measurements))
    print('n_measurements: ', n_measurements)

if __name__ == '__main__':
    main()
