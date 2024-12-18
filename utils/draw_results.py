import cv2
import mediapipe as mp
import json
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

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

def load_colors(path_to_colors:str, path_to_connections:str):
    """
    Loads colors json as a dict
    """
    finger_color_dict = json.load(open(path_to_colors, 'r'))
    hierarchy_dict = json.load(open(path_to_connections, 'r'))
    joint_color_dict = {}
    joint_color_dict[hierarchy_dict['wrist']] = str_to_color(finger_color_dict['wrist'])
    for finger_name, connections in hierarchy_dict['fingers'].items():
        for joint_id in connections:
            joint_color_dict[joint_id] = str_to_color(finger_color_dict[finger_name])
    return joint_color_dict



def draw_hand_landmarks_on_live(detection_result, rgb_image, _):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    rgb_image = rgb_image.numpy_view()
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
      hand_landmarks = hand_landmarks_list[idx]
      handedness = handedness_list[idx]

      # Draw the hand landmarks.
      hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
      hand_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
      ])
      solutions.drawing_utils.draw_landmarks(
        annotated_image,
        hand_landmarks_proto,
        solutions.hands.HAND_CONNECTIONS,
        solutions.drawing_styles.get_default_hand_landmarks_style(),
        solutions.drawing_styles.get_default_hand_connections_style())

      # Get the top left corner of the detected hand's bounding box.
      height, width, _ = annotated_image.shape
      x_coordinates = [landmark.x for landmark in hand_landmarks]
      y_coordinates = [landmark.y for landmark in hand_landmarks]
      text_x = int(min(x_coordinates) * width)
      text_y = int(min(y_coordinates) * height) - MARGIN

      # Draw handedness (left or right hand) on the image.
      cv2.putText(annotated_image, f"{handedness[0].category_name}",
                  (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                  FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    cv2.imshow('huh', annotated_image)
    return

def draw_detection_result(image, landmarks, hierarchy_dict, color_dict):
    width, height, _ = image.shape
    for hand in landmarks:
        for landmark_id in range(len(hand)):
            cur_landmark = hand[landmark_id]
            landmark_connections = hierarchy_dict[landmark_id]
            landmark_x = int(width*cur_landmark.x)
            landmark_y = int(height*cur_landmark.y)
            for connection_idx in landmark_connections:
                connection = hand[connection_idx]
                connection_x = int(connection.x * width)
                connection_y = int(connection.y * height)
                cv2.line(
                    img=image, 
                    pt1=(landmark_x, landmark_y), 
                    pt2=(connection_x, connection_y),
                    color=color_dict[connection_idx],
                    thickness=4 
                    )
            cv2.circle(
                img=image,
                center=(landmark_x, landmark_y),
                color=(255, 0, 255),
                radius=3,
                thickness=-1
            )