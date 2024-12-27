import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import argparse
from utils.draw_results import load_connections, load_colors, draw_detection_result, draw_hand_landmarks_on_live
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_type', help='defines type of input stream: video or camera', choices=('cam', 'vid'))
    parser.add_argument('sources', help='list of input sources', nargs='+')
    parser.add_argument('-dev', '--by-dev', help='Specifies whether cameras sould be identified by their file in /dev', required=False, action='store_true')
    parser.add_argument('-b', '--buffer-size', help='Specifies buffer size for input streams', type=int, default=4)
    parser.add_argument('-fps', '--framerate', help='Specifies desired framerate', type=int, default=30)
    args = parser.parse_args()

    caps = list()
    buffer_size = args.buffer_size
    framerate = args.framerate
    source_type = args.source_type
    if source_type == 'cam':
        for source in args.sources:
            if not args.by_dev:
                source = int(source)
            cur_cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
            cur_cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            caps.append(cur_cap)
    else:
        for source in args.sources:
            cur_cap = cv2.VideoCapture(source)
            cur_cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            caps.append(cur_cap)

    # model setup
    model_path = 'hand_landmarker.task'
    base_options = mp.tasks.BaseOptions
    hand_landmarker = mp.tasks.vision.HandLandmarker
    hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
    vision_running_mode = mp.tasks.vision.RunningMode
    if source_type ==  'cam':
        vision_running_mode = vision_running_mode.LIVE_STREAM
    else:
        options = hand_landmarker_options(
            base_options=base_options(model_asset_path=model_path),
            running_mode=vision_running_mode.VIDEO,
            num_hands=1
        )

    # load dicts for drawing
    hierarchy_dict = load_connections('hand_config/hand_connections.json')
    colors_dict = load_colors('hand_config/hand_colors.json', 'hand_config/hand_connections.json')

    # set list of constant size
    rets = [True for _ in caps]
    print(caps)
    with hand_landmarker.create_from_options(options) as landmarker:
        while (np.all(rets)):
            # time measurements to calculate FPS
            start = time.time()
            
            # Capture frames from all sources
            for source_idx in range(len(caps)):
                rets[source_idx], cur_frame = caps[source_idx].read() 
                
                cur_frame = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2RGB)
                # detect hand
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cur_frame)
                if source_type == 'cam':
                    landmarker.detect_async(mp_image, int(time.time()*1000))
                else:
                    landmarker.detect_for_video(mp_image, int(time.time()*1000))
                # result2 = landmarker.detect(mp_image2)
                # draw_detection_result(cur_frame, result1.hand_landmarks, hierarchy_dict, colors_dict)
                # Display the resulting frame
                # cv2.imshow(f'source {source_idx}', cv2.cvtColor(cur_frame, cv2.COLOR_RGB2BGR))
            
            end = time.time()
            print(f'FPS: {1/(end - start)}')
            if cv2.waitKey(int(1/framerate*1000)) == 27:
                break

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows() 

if __name__ == '__main__':
    main()