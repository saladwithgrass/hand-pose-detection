import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import argparse
from utils.draw_results import load_connections, load_colors, draw_detection_result



def main():
    print(mp.solutions.hands.HAND_CONNECTIONS)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c1', '--camera1', help='camera 1 id')
    parser.add_argument('-c2', '--camera2', help='camera 2 id')
    args = parser.parse_args()
    cam1_id = int(args.camera1)
    cam2_id = int(args.camera2)
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
        cap1 = cv2.VideoCapture(cam1_id)
        cap2 = cv2.VideoCapture(cam2_id)
        while (cap1.isOpened() and cap2.isOpened()):
            # Capture frame-by-frame
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

            # detect hand
            mp_image1 = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame1)
            mp_image2 = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame2)
            result1 = landmarker.detect(mp_image1)
            result2 = landmarker.detect(mp_image2)
            draw_detection_result(frame1, result1.hand_landmarks, hierarchy_dict, colors_dict)
            draw_detection_result(frame2, result2.hand_landmarks, hierarchy_dict, colors_dict)
            # resize for displaying
            # frame = cv2.resize(
            #     frame, (540, 380), fx = 0, fy = 0,
            #     interpolation = cv2.INTER_CUBIC
            #     )

            # Display the resulting frame
            cv2.imshow('Frame1', cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR))
            cv2.imshow('Frame2', cv2.cvtColor(frame2, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(25) == 27:
                break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows() 

if __name__ == '__main__':
    main()