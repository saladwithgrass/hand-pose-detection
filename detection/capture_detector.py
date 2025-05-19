import mediapipe as mp
import cv2
import numpy as np

# SECTION INIT_CAP BEGIN
class CaptureDetector():

    def __init__(
        self,
        capture:cv2.VideoCapture,
        model_path:str='detection/hand_landmarker.task'
    ):

        # add capture to a class member
        self.cap:cv2.VideoCapture = capture

        # get image size
        self.image_size = (
            capture.get(cv2.CAP_PROP_FRAME_WIDTH),
            capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
# SECTION INIT_CAP END

# SECTION INIT_TASK BEGIN
        # create options for landmarker
        base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
        hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
        running_mode = mp.tasks.vision.RunningMode.VIDEO
        self.options = hand_landmarker_options(
            base_options=base_options,
            running_mode=running_mode,
            num_hands=1
        )

        landmarker = mp.tasks.vision.HandLandmarker
        self.landmarker = landmarker.create_from_options(self.options)
# SECTION INIT_TASK END

# SECTION FRAME_PREPROCESS BEGIN
    def process_one_frame(self, return_frame:bool=True):
        # read frame
        ret, frame = self.cap.read()
        
        # check if read happened
        if not ret:
            print('OUT OF FRAMES')
            raise Exception()

        # convert to rgb
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # mediapipe image processing
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
            )
# SECTION FRAME_PREPROCESS END

# SECTION GET_TIME BEGIN
        # add timestamp
        timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
# SECTION GET_TIME END

# SECTION GET_DETECTION BEGIN
        # get detection result
        detection_result = self.landmarker.detect_for_video(
            mp_image,
            int(timestamp_ms)
        )
# SECTION GET_DETECTION END

# SECTION FRAME_CONVERSION BEGIN
        if return_frame:
            # convert back to rgb
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
        else:
            frame = None
# SECTION FRAME_CONVERSION END

# SECTION DETECTION_CHECK BEGIN
        if len(detection_result.hand_landmarks) == 0:
            return [], frame
# SECTION DETECTION_CHECK END

# SECTION RESULT_PREPARATION BEGIN
        landmarks = detection_result.hand_landmarks[0]
        points_array = np.zeros((len(landmarks), 2), dtype=np.int16)
        for idx in range(len(landmarks)):
            points_array[idx] = [
                int(landmarks[idx].x * self.image_size[0]),
                int(landmarks[idx].y * self.image_size[1])
                ]
        
        # return landmarks
        return points_array, frame
# SECTION RESULT_PREPARATION END

# SECTION DESTRUCTOR BEGIN
    def __del__(self):
        self.landmarker.close()
        self.cap.release()
# SECTION DESTRUCTOR END

