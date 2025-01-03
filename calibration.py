import cv2
import numpy as np
import argparse
import pickle

def generate_3d_points_for_marker(size_m:float):
    """
    Generates a 4x3 matrix of marker coordinates on a flat plane.
    Center of the marker is (0, 0, 0).
    """
    half_size = size_m / 2
    points = [
        [-half_size, half_size, 0], # lu
        [half_size, half_size, 0], # ru
        [half_size, -half_size, 0], #rb
        [-half_size, -half_size, 0.] # lb
        ]
    return np.array(points, dtype=np.float32)
    
def detect_aruco_in_image(image, parameters, dictionary_name):
    """
    Detects aruco marker in an image with given parameters.
    Returns only corners and ids.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_name)
    corners, ids, _ = cv2.aruco.detectMarkers(
        gray, 
        dictionary=dictionary,
        parameters=parameters
        )
    return np.array(corners, dtype=np.float32), ids

def main():
    # add CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('camera_id', help='camera id in /dev/video*')
    parser.add_argument('-ms', '--marker-size', help='Length of one side of the detection of a square marker in meters.', default=0.1)
    parser.add_argument('-b', '--buffer-size', help='Specifies buffer size for input streams', type=int, default=10)
    args = parser.parse_args()
    buffer_size = args.buffer_size
    source_id = int(args.camera_id)

    # open camera for reading 
    cap = cv2.VideoCapture(source_id, cv2.CAP_V4L2)
    # set buffer size
    cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

    # specify aruco dictionary    
    aruco_dictionary = cv2.aruco.DICT_4X4_50
    # create detector parameters
    aruco_detector_parameters = cv2.aruco.DetectorParameters()
    aruco_detector_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX

    # create a generic matrix for marker coordinates
    aruco_points = generate_3d_points_for_marker(0.1)
    
    # create empty arrays to store
    object_points = []
    image_points = []

    frame_counter = 0
    while True:
        # capture frame
        ret, frame = cap.read()
        
        # check success
        if not ret:
            break
        
        # detect aruco
        detected_corners, ids = detect_aruco_in_image(frame, aruco_detector_parameters, aruco_dictionary)
        if detected_corners.size > 0: 
            # draw detection if it exists
            cv2.aruco.drawDetectedMarkers(frame, detected_corners, ids, borderColor=(255, 0, 255))

        # show detection
        cv2.imshow('detection', frame)

        key = cv2.waitKey(10)
        if key == ord('c'):
            frame_counter += 1
            print(f'frames captured: {frame_counter}')
            # add points to calibration arrays
            object_points.append(aruco_points)
            # important. reshape detected corners from (1, 4, 2) to (4, 2)
            image_points.append(detected_corners.reshape((4, 2)))
        elif key == ord('q'):
            break


    print('running calibrations...', end='', flush=True)
    # run calibrations
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objectPoints=object_points, 
        imagePoints=image_points, 
        imageSize=frame.shape[0:2][::-1],
        cameraMatrix=None,
        distCoeffs=None
        )
    
    print('Done.')

    # simple data structure for convenience
    calibration_data = {
        'camera_matrix': camera_matrix,
        'dist_coeffs': dist_coeffs,
        'rvecs': rvecs,
        'tvecs': tvecs
    }

    # save file
    with open(f'calibration_{source_id}.pkl', 'wb') as out_file:
        print(f'saving data for capture with id {source_id} in calibration{source_id}.pkl...', end='', flush=True)
        pickle.dump(
            obj=calibration_data,
            file=out_file
        )
        print('Done!')

    
if __name__ == '__main__':
    main()