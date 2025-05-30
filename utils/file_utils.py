import pickle
import json
import cv2
import glob
import numpy as np

def load_json_as_dict(path:str) -> dict:
    with open(path, 'r') as input_file:
        result = json.load(input_file)
        return result

def load_charuco_parameters(json_path:str):
    """
    Return charuco parameters as a tuple in the following order:
    BOARD_ROWS, BOARD_COLS, SQUARE_SIZE, MARKER_SIZE, ARUCO_DICTIONARY.
    """
    params_dict = load_json_as_dict(json_path)
    dict_aruco = getattr(cv2.aruco, params_dict["DICT_NAME"])
    loaded_dict = cv2.aruco.getPredefinedDictionary(dict_aruco)
    return params_dict['BOARD_ROWS'],  \
           params_dict['BOARD_COLS'],  \
           params_dict['SQUARE_SIZE'], \
           params_dict['MARKER_SIZE'], \
           loaded_dict
    
def create_charuco_from_json(json_path:str='config/charuco_parameters.json') -> cv2.aruco.CharucoBoard:

    # load aruco parameters
    CHARUCO_BOARD_ROWS, \
    CHARUCO_BOARD_COLS, \
    CHARUCO_SQUARE_SIZE,\
    CHARUCO_MARKER_SIZE,\
    ARUCO_DICTIONARY = load_charuco_parameters(json_path)

    # create board
    charuco_board = cv2.aruco.CharucoBoard(
        size=(CHARUCO_BOARD_COLS, CHARUCO_BOARD_ROWS),
        squareLength=CHARUCO_SQUARE_SIZE,
        markerLength=CHARUCO_MARKER_SIZE,
        dictionary=ARUCO_DICTIONARY
    )
    charuco_board.setLegacyPattern(True)
    return charuco_board

def create_capture_from_json(dev_id:int, json_path:str) -> cv2.VideoCapture:
    params_dict = load_json_as_dict(json_path)
    
    cap = cv2.VideoCapture(dev_id, cv2.CAP_V4L2)
    for name, value in params_dict.items():
        # if its fourcc, generate it
        if name == 'CAP_PROP_FOURCC':
            fcc_code = cv2.VideoWriter.fourcc(value[0], value[1], value[2], value[3])
            cap.set(cv2.CAP_PROP_FOURCC, fcc_code)
            continue
        cap.set(getattr(cv2, name), value)
    return cap
    
def load_camera_intrinsics(path_to_file:str):
    with open(path_to_file, 'rb') as intr_file:
        intr_dict = pickle.load(intr_file)
        cam_matrix = intr_dict['camera_matrix']
        dist_coeffs = intr_dict['dist_coeffs']
        width = intr_dict['image_width']
        height = intr_dict['image_height']
        return cam_matrix, dist_coeffs, width, height

def load_intr_with_minimal_error(cam_id:str):
    candidates = glob.glob(f'../calibration_data/calibration_{cam_id}*.pkl')
    error_kw = 'error='

    candidates_with_errors = {}

    for candidate in candidates:
        error_position = candidate.find(error_kw)
        error_string = candidate.removesuffix('.pkl')[error_position + len(error_kw):]
        if error_string.isnumeric():
            candidates_with_errors[float(error_string)] = candidate
    
    min_error = np.min(list(candidates_with_errors.keys()))
    selected_candidate = candidates_with_errors[min_error]
    return selected_candidate
    
