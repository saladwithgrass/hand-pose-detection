import numpy as np
import cv2
import pickle

class CameraTriangulator():

    def __init__(self, 
                    camera_matrices:list[np.ndarray],
                    distortion_coefficients:list[np.ndarray],
                    cameras_rvecs:list[np.ndarray],
                    cameras_tvecs:list[np.ndarray],
                    image_height:int,
                    image_width:int
                ):
        # create self fields
        self.camera_matrices = camera_matrices
        self.dist_coeffs = distortion_coefficients
        self.rvecs = cameras_rvecs
        self.tvecs = cameras_tvecs
        self.image_size = (image_height, image_width)
        self.new_cam_matrices = []
        self.undistortMaps = []
        self.projection_matrices = []

        # create new optimal camera matrices
        for cam_matrix, dist_coeffs in zip(camera_matrices, distortion_coefficients):
            new_cam_matrix, roi = cv2.getOptimalNewCameraMatrix(
                cameraMatrix=cam_matrix, 
                distCoeffs=dist_coeffs, 
                imageSize=self.image_size
                )
            self.new_cam_matrices.append(new_cam_matrix)
            print(cam_matrix)
            print(new_cam_matrix)
            print(' ')
            self.undistortMaps.append(cv2.initUndistortRectifyMap(
                cameraMatrix=cam_matrix,
                distCoeffs=dist_coeffs,
                R=cv2.Mat(),
                newCameraMatrix=new_cam_matrix,
                size=self.image_size,
                m1type=cv2.CV_32FC1
            ))

        # create projection matrices
        for cam_matrix, rvec, tvec in zip(camera_matrices, cameras_rvecs, cameras_tvecs):
            self.projection_matrices.append(self.create_projection_matrix(rvec, tvec, cam_matrix))

    def create_projection_matrix(self, rvec, tvec, cam_matrix):
        result = np.hstack((cv2.Rodrigues(rvec)[0], tvec))
        reuslt = np.dot(cam_matrix, result)
        return result

    def triangulate(self, pixel_positions):
        pass

def create_triangulator_from_files(
        intr_files:list[str],
        orientation_files:list[str]
        ):
    cam_matrices = []
    dist_coeffs = []
    rvecs = []
    tvecs = []
    for intr_filename, orientation_filename in zip(intr_files, orientation_files):
        with open(intr_filename, 'rb') as intr_file, \
        open(orientation_filename, 'rb') as orientation_file:
            
            # load dictionaries
            cur_intr = pickle.load(intr_file)
            cur_orientation = pickle.load(orientation_file)
            
            # read parameters
            print(cur_intr)
            cur_cam_matrix = cur_intr['camera_matrix']
            cur_dist_coeffs = cur_intr['dist_coeffs']
            cur_rvec = cur_orientation['rvec']
            cur_tvec = cur_orientation['tvec']

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
        cameras_tvecs=tvecs
        )
            

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-if', '--intrinsics', nargs='+')
    parser.add_argument('-or', '--orientation', nargs='+')
    args = parser.parse_args()

    create_triangulator_from_files(args.intrinsics, args.orientation)