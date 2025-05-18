import cv2
import mediapipe as mp
import json
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import matplotlib.colors as mcolors

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def load_connections(path:str):
    """
    Loads hand landmark hierarchy as a dict.
    """
    hand_dict = json.load(open(path, 'r'))
    wrist_id = hand_dict['wrist']
    fingers = hand_dict['fingers']
    hierarchy_dict = dict()
    hierarchy_dict[wrist_id] = []
    for finger_name, joints in fingers.items():
        hierarchy_dict[wrist_id].append(joints[0])
        for joint_idx in range(len(joints)-1):
            if joints[joint_idx] in hierarchy_dict.keys():
                hierarchy_dict[joints[joint_idx]].append(joints[joint_idx + 1])
            else:
                hierarchy_dict[joints[joint_idx]] = [joints[joint_idx + 1]]
        hierarchy_dict[joints[-1]] = []
    return hierarchy_dict

def str_to_color(color_str:str):
    color_str = color_str.replace('#', '')
    return (int(color_str[0:2], 16), int(color_str[2:4], 16), int(color_str[4:6], 16))

def load_colors(path_to_colors:str, path_to_hierarchy:str):
    """
    Loads colors json as a dict.
    The key is color name, the value are the joint indeces
    """
    finger_color_dict = json.load(open(path_to_colors, 'r'))
    hierarchy_dict = json.load(open(path_to_hierarchy, 'r'))
    joint_color_dict = {}
    joint_color_dict[finger_color_dict['wrist']] = [0]
    for finger_name, connections in hierarchy_dict['fingers'].items():
        joint_color_dict[finger_color_dict[finger_name]] = connections
        # append to wrist
        joint_color_dict[finger_color_dict['wrist']].append(connections[0])
    # make wrist cyclical
    joint_color_dict[finger_color_dict['wrist']].append(joint_color_dict[finger_color_dict['wrist']][0])
    return joint_color_dict

def draw_hand_on_image(image, landmarks, color_dict:dict, hierarchy_dict:dict):
    for color, indexes in color_dict.items():
        cur_color = mcolors.to_rgb(color)
        cur_color = tuple(int(x * 255) for x in cur_color)
        # stupid rgb to bgr conversion
        cur_color = (cur_color[2], cur_color[1], cur_color[0])
        for index in indexes:
            if index >= len(landmarks):
                continue
            cv2.circle(
                img=image,
                center=landmarks[index],
                radius=5,
                color=cur_color,
                thickness=-1
            )
            
            # draw connections if they exist
            for connection_idx in hierarchy_dict[index]:
                cv2.line(
                    img=image,
                    pt1=landmarks[index],
                    pt2=landmarks[connection_idx],
                    color=cur_color,
                    thickness=2
                )

def draw_text(img:np.ndarray, text:str):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, img.shape[0] - 10)
    fontScale              = 2
    fontColor              = (0,255,0)
    thickness              = 3
    lineType               = 2
    
    cv2.putText(img, text,
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)

