import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import argparse
from utils.draw_results import load_connections, load_colors, draw_detection_result



def main():
    print(mp.solutions.hands.HAND_CONNECTIONS)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='path to input video')
    args = parser.parse_args()
    input_path = args.input
    model_path = '/home/vix/Documents/bachelor_thesis/hand-pose-detection/hand_landmarker.task'
    base_options = mp.tasks.BaseOptions
    hand_landmarker = mp.tasks.vision.HandLandmarker
    hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
    vision_running_mode = mp.tasks.vision.RunningMode
    options = hand_landmarker_options(
        base_options=base_options(model_asset_path=model_path),
        running_mode=vision_running_mode.IMAGE
    )
    hierarchy_dict = load_connections('hand_config/hand_connections.json')
    colors_dict = load_colors('hand_config/hand_colors.json', 'hand_config/hand_connections.json')
    with hand_landmarker.create_from_options(options) as landmarker:
        cap = cv2.VideoCapture(input_path)

        while (cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # detect hand
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect(mp_image)
            draw_detection_result(frame, result.hand_landmarks, hierarchy_dict, colors_dict)

            # resize for displaying
            # frame = cv2.resize(
            #     frame, (540, 380), fx = 0, fy = 0,
            #     interpolation = cv2.INTER_CUBIC
            #     )

            # Display the resulting frame
            cv2.imshow('Frame', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(25) == 27:
                break

    cap.release()
    cv2.destroyAllWindows() 

if __name__ == '__main__':
    main()