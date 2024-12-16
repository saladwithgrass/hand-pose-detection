import cv2
import mediapipe as mp
import json

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
        print(len(joints))
        hierarchy_dict[joints[-1]] = []
    return hierarchy_dict

def draw_detection_result(image, landmarks, hierarchy_dict):
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
                    color=(0, 255, 255),
                    thickness=1 
                    )
            cv2.circle(
                img=image,
                center=(landmark_x, landmark_y),
                color=(255, 0, 255),
                radius=3,
                thickness=-1
            )