import mediapipe as mp
import time
import cv2
import numpy as np
from utils.draw_results import (
    load_colors, load_connections, draw_detection_result
)

class CaptureDetector():

    def __init__(self, model_path:str, capture:cv2.VideoCapture):
        # add capture to a class member
        self.cap:cv2.VideoCapture = capture

        # load hand connections
        self.hierarchy_dict = load_connections('hand_config/hand_connections.json')
        # load finger colors
        self.color_dict = load_colors('hand_config/hand_colors.json', 'hand_config/hand_connections.json')

        # create options for landmarker
        base_options = mp.tasks.BaseOptions
        hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
        running_mode = mp.tasks.vision.RunningMode.VIDEO
        self.options = hand_landmarker_options(
            base_options=base_options(model_asset_path=model_path),
            running_mode=running_mode,
            num_hands=1
        )

        landmarker = mp.tasks.vision.HandLandmarker
        self.landmarker = landmarker.create_from_options(self.options)

    def process_one_frame(self):
        # read frame
        ret, frame = self.cap.read()
        
        # check if read happened
        if not ret:
            print('OUT OF FRAMES')
            return None

        # convert to rgb
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # mediapipe image processing
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
            )

        # add timestamp
        timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)

        # get detection result
        detection_result = self.landmarker.detect_for_video(
            mp_image,
            int(timestamp_ms)
        )

        # draw detection result
        draw_detection_result(
            image=frame, 
            landmarks=detection_result.hand_landmarks,
            hierarchy_dict=self.hierarchy_dict,
            color_dict=self.color_dict
            )
        
        # convert back to bgr
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame
        


    def __del__(self):
        self.landmarker.close()
        self.cap.release()
