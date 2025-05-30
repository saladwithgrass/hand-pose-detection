import os
import cv2
import json
import numpy as np
import matplotlib.colors as mcolors

from utils.file_utils import load_json_as_dict

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def load_connections(path:str='config/hand_connections.json'):
    """
    Loads hand landmark hierarchy as a dict.
    """
    print(os.getcwd())
    hand_dict = json.load(open(path, 'r'))
    wrist_id = hand_dict['wrist']
    fingers = hand_dict['fingers']
    hierarchy_dict = dict()
    hierarchy_dict[wrist_id] = []
    for _, joints in fingers.items():
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

def load_colors_and_connections(path_to_colors:str, path_to_hierarchy:str):
    """
    Loads colors and coonnection jsons as a dict.
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

    return joint_color_dict, hierarchy_dict

def join_colors_and_connections(
        connections_dict:dict
    ):

    result = {}
    colors = load_json_as_dict('config/hand_colors.json')

    # create wrist pairs
    connections_from_wrist = []
    for finger_name, finger_joints in connections_dict['fingers'].items():
        first_finger_joint = finger_joints[0]
        connections_from_wrist.append([connections_dict['wrist'], first_finger_joint])
    result[colors['wrist']] = connections_from_wrist

    # create connections for each finger
    for finger_name, finger_joints in connections_dict['fingers'].items():
        cur_finger_connections = list()
        for joint in range(len(finger_joints)-1):
            cur_finger_connections.append([
                finger_joints[joint], 
                finger_joints[joint+1]
            ])
        result[colors[finger_name]] = cur_finger_connections
    return result

print('Loading colors and connections')
connections_dict = load_json_as_dict('config/hand_connections.json')
draw_dict = join_colors_and_connections(connections_dict)

def draw_hand_on_image(
    image, 
    landmarks
):
    if len(landmarks) == 0:
        return
    for cur_color, connections in draw_dict.items():
        bgr_color = mcolors.to_rgb(cur_color)
        bgr_color = tuple(int(x * 255) for x in bgr_color)
        for cur_connection in connections:
            cv2.circle(
                img=image,
                center=landmarks[cur_connection[0]],
                radius=5,
                color=bgr_color,
                thickness=-1
            )
            cv2.line(
                img=image,
                pt1=landmarks[cur_connection[0]],
                pt2=landmarks[cur_connection[1]],
                color=bgr_color,
                thickness=2
            )

def visualize_basic_gripper(image, detection_result, draw_names:bool=False):
    if len(detection_result) < 8:
        return
    index_points = np.array([detection_result[5], detection_result[8]], int)
    thumb_points = np.array([detection_result[2], detection_result[4]], int)
    begin_center = ((index_points[0] + thumb_points[0]) / 2).astype(int)
    end_center = ((index_points[1] + thumb_points[1]) / 2).astype(int)
    print(begin_center.dtype)
    # draw midpoints
    cv2.circle(
        image,
        center=begin_center,
        color=(255, 0, 0),
        radius=10,
        thickness=-1
    )
    cv2.circle(
        image,
        center=end_center,
        color=(255, 0, 0),
        radius=10,
        thickness=-1
    )
    # draw gripper fingers
    cv2.line(
        image,
        begin_center,
        index_points[1],
        color=(255, 200, 200),
        thickness=3
    )
    cv2.line(
        image,
        begin_center,
        thumb_points[1],
        color=(255, 200, 200),
        thickness=3
    )

    cv2.line(
        image,
        end_center,
        begin_center,
        color=(255, 0, 0),
        thickness=5
    )

    # draw index points
    cv2.circle(
        image,
        center=index_points[0],
        color=(0, 0, 255),
        radius=10,
        thickness=-1
    )
    cv2.circle(
        image,
        center=index_points[1],
        color=(0, 0, 255),
        radius=10,
        thickness=-1
    )
    # draw thumb
    cv2.circle(
        image,
        center=thumb_points[0],
        color=(0, 255, 0),
        radius=10,
        thickness=-1
    )
    cv2.circle(
        image,
        center=thumb_points[1],
        color=(0, 255, 0),
        radius=10,
        thickness=-1
    )
    if not draw_names:
        return
    draw_text(
        img=image,
        text='B',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=begin_center
    )
    draw_text(
        img=image,
        text='E',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=end_center
    )
    draw_text(
        img=image,
        text='Ib',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=index_points[0]
    )
    draw_text(
        img=image,
        text='Ie',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=index_points[1]
    )
    draw_text(
        img=image,
        text='Tb',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=thumb_points[0]
    )
    draw_text(
        img=image,
        text='Te',
        fontColor=(255, 255, 255),
        bottomLeftCornerOfText=thumb_points[1]
    )

def draw_text(
    img:np.ndarray, 
    text:str, 
    fontColor=(0,255,0),
    bottomLeftCornerOfText=None,
    fontScale=2,
):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    if bottomLeftCornerOfText is None:
        bottomLeftCornerOfText = (10, img.shape[0] - 10)
    thickness              = 3
    lineType               = 2
    
    cv2.putText(img, text,
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)

