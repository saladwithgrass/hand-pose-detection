from tqdm import tqdm
import cv2
import numpy as np
import argparse
import pickle

def generate_3d_points_for_marker(size_m:float):
    half_size = size_m / 2
    points = [
        [-half_size, half_size, 0], # lu
        [half_size, half_size, 0], # ru
        [half_size, -half_size, 0], #rb
        [-half_size, -half_size, 0.] # lb
        ]
    return np.array(points)
    
def detect_aruco_in_image(image, parameters, dictionary_name):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_name)
    corners, ids, _ = cv2.aruco.detectMarkers(
        gray, 
        dictionary=dictionary,
        parameters=parameters
        )
    return np.array(corners), ids

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('camera_id', help='camera id in /dev/video*')
    parser.add_argument('-ms', '--marker-size', help='Length of one side of the detection of a square marker in meters.', default=0.1)
    parser.add_argument('-b', '--buffer-size', help='Specifies buffer size for input streams', type=int, default=10)
    args = parser.parse_args()
    buffer_size = args.buffer_size
    source_id = int(args.camera_id)

    cap = cv2.VideoCapture(source_id, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

    aruco_dictionary = cv2.aruco.DICT_4X4_50
    aruco_detector_parameters = cv2.aruco.DetectorParameters()
    aruco_detector_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX

    aruco_points = generate_3d_points_for_marker(0.1)

    object_points = []
    image_points = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detected_corners, ids = detect_aruco_in_image(frame, aruco_detector_parameters, aruco_dictionary)
        if detected_corners.size <= 0:
            continue
        
        object_points.append(aruco_points)
        image_points.append(detected_corners)

        cv2.imshow('detection', frame)
        if cv2.waitKey(10) == 27:
            break

    # object_points = np.array(object_points)

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objectPoints=object_points, 
        imagePoints=image_points, 
        imageSize=frame.shape[0:2][::-1],
        cameraMatrix=None,
        distCoeffs=None
        )
    calibration_data = {
        'camera_matrix': camera_matrix,
        'dist_coeffs': dist_coeffs,
        'rvecs': rvecs,
        'tvecs': tvecs
    }
    with open(f'calibration_{source_id}.pkl', 'w'):
        print(f'data for capture with id {source_id} saved in calibration{source_id}.pkl')
        pickle.dump(calibration_data)
    


    

if __name__ == '__main__':
    main()