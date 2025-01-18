import mediapipe as mp
import time
import cv2
import numpy as np

class CaptureDetector():

    def __init__(self, capture:cv2.VideoCapture, model_path:str='hand_landmarker.task'):

        # add capture to a class member
        self.cap:cv2.VideoCapture = capture

        # get image size
        self.image_size = (
            capture.get(cv2.CAP_PROP_FRAME_WIDTH),
            capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

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
            return np.array([])

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

        # convert back to rgb
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if len(detection_result.hand_landmarks) == 0:
            return [], frame

        landmarks = detection_result.hand_landmarks[0]
        points_array = [(0, 0)] * len(landmarks)
        for idx in range(len(landmarks)):
            points_array[idx] = (
                int(landmarks[idx].x * self.image_size[0]),
                int(landmarks[idx].y * self.image_size[1])
                )
        

        # return landmarks
        return points_array, frame

    def __del__(self):
        self.landmarker.close()
        self.cap.release()
