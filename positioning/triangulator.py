import numpy as np
import cv2
import pickle

import sys
sys.path.append('../')
from utils.file_utils import create_capture_from_json

class CameraTriangulator():

    def __init__(self, 
                    camera_matrices:list[np.ndarray],
                    distortion_coefficients:list[np.ndarray],
                    cameras_rvecs:list[np.ndarray],
                    cameras_tvecs:list[np.ndarray],
                    image_width:int,
                    image_height:int
                ):
        # create self fields
        self.camera_matrices = camera_matrices
        self.dist_coeffs = distortion_coefficients
        self.rvecs = cameras_rvecs
        self.tvecs = cameras_tvecs
        self.image_size = (image_width, image_height)
        self.new_cam_matrices = []
        self.undistortMaps = []
        self.projection_matrices = []

        # create new optimal camera matrices and undistort maps
        for cam_matrix, dist_coeffs in zip(camera_matrices, distortion_coefficients):
            new_cam_matrix, roi = cv2.getOptimalNewCameraMatrix(
                cameraMatrix=cam_matrix, 
                distCoeffs=dist_coeffs, 
                imageSize=self.image_size,
                alpha=0.5
                )
            self.new_cam_matrices.append(new_cam_matrix)
            self.undistortMaps.append(cv2.initUndistortRectifyMap(
                cameraMatrix=cam_matrix,
                distCoeffs=dist_coeffs,
                R=None,
                newCameraMatrix=new_cam_matrix,
                size=self.image_size,
                m1type=cv2.CV_32FC1
            ))

        # create projection matrices
        for cam_matrix, rvec, tvec in zip(camera_matrices, cameras_rvecs, cameras_tvecs):
            self.projection_matrices.append(self.create_projection_matrix(rvec, tvec, cam_matrix))

    def create_projection_matrix(self, rvec, tvec, cam_matrix):
        print('rvec:')
        print(cv2.Rodrigues(rvec)[0])
        print('tvec:')
        print(tvec)
        result = np.hstack((cv2.Rodrigues(rvec)[0], tvec))
        print('rt matrix:')
        print(result)
        print()
        result = cam_matrix @ result # be not afraid, sinner, this is just numpy matrix multiplication
        return result

    def undistort_image(self, image, camera_index):
        map1, map2 = self.undistortMaps[camera_index]
        return cv2.remap(image, map1=map1, map2=map2, interpolation=cv2.INTER_LINEAR)

    def undistort_point(self, point:tuple[int, int], camera_index):
        map1, map2 = self.undistortMaps[camera_index]
        x = point[0]
        y = point[1]
        print(map1[y, x])
        # x_undistorted = map1[y_distorted, x_distorted][0]
        # y_undistorted = map2[y_distorted, x_distorted][0]
        return (int(map1[y, x]), int(map2[y, x]))

    def triangulate(self, pixel_positions=None):
        
        # construct matrix for solving DLT
        DLT_equations = []
        for point, projection_matrix in zip(pixel_positions, self.projection_matrices):
            p1, p2, p3 = tuple(projection_matrix)
            u = point[0]
            v = point[1]
            eq1 = v * p1 - p2
            eq2 = p1 - u * p3
            DLT_equations.append(eq1)
            DLT_equations.append(eq2)
        
        # convert to np.array for convenience
        DLT_matrix = np.array(DLT_equations)

        # decompose matrix
        U, S, vh = np.linalg.svd(DLT_matrix.T @ DLT_matrix)

        # get last column
        result = vh[3, 0:3] / vh[3, 3]
        return result


def create_triangulator_from_files(
        intr_files:list[str],
        orientation_files:list[str]
        ):
    cam_matrices = []
    dist_coeffs = []
    rvecs = []
    tvecs = []
    for intr_filename, orientation_filename in zip(intr_files, orientation_files):
        image_size = None
        with open(intr_filename, 'rb') as intr_file, \
        open(orientation_filename, 'rb') as orientation_file:
            
            # load dictionaries
            cur_intr = pickle.load(intr_file)
            cur_orientation = pickle.load(orientation_file)
            
            # read parameters
            cur_cam_matrix = cur_intr['camera_matrix']
            cur_dist_coeffs = cur_intr['dist_coeffs']
            cur_image_width = cur_intr['image_width']
            cur_image_height = cur_intr['image_height']
            cur_image_size = (cur_image_width, cur_image_height)
            cur_rvec = cur_orientation['rvec']
            cur_tvec = cur_orientation['tvec']

            # check if image sizes are the same
            if image_size is not None and image_size != cur_image_size:
                print('ERROR: image sizes must be the same. Aborting.')
                exit(1)
            else:
                image_size = cur_image_size
                print(f'Image size is {image_size}')

            # save them to arrays
            cam_matrices.append(cur_cam_matrix)
            dist_coeffs.append(cur_dist_coeffs)
            rvecs.append(cur_rvec)
            tvecs.append(cur_tvec)
    
    # create and return triangulator
    return CameraTriangulator(
        camera_matrices=cam_matrices,
        distortion_coefficients=dist_coeffs,
        cameras_rvecs=rvecs,
        cameras_tvecs=tvecs,
        image_width=image_size[0],
        image_height=image_size[1]
        )
            

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-if', '--intrinsics', nargs='+')
    parser.add_argument('-or', '--orientation', nargs='+')
    args = parser.parse_args()

    triangulator = create_triangulator_from_files(args.intrinsics, args.orientation)

    point1 = (1000, 500)
    point2 = (100, 800)

    triangulator.triangulate([point1, point2])
    exit(0)

    cap = create_capture_from_json(2, '../config/capture_params.json')

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        undistorted = triangulator.undistort_image(frame, 0)
        cv2.imshow('undistorted', cv2.resize(undistorted, dsize=None, fx=0.5, fy=0.5))
        if cv2.waitKey(10) == 27:
            break