import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import argparse
from utils.draw_results import load_connections, load_colors, draw_detection_result, draw_hand_landmarks_on_live
import numpy as np
import sys

def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def create_options(type:str):
    # model setup
    model_path = 'hand_landmarker.task'
    base_options = mp.tasks.BaseOptions
    hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
    vision_running_mode = mp.tasks.vision.RunningMode
    
    # initialize options for correct mode
    if type == 'cam' or type == 'vid':
        running_mode = vision_running_mode.VIDEO
        callback = None
    else:
        error('UNKNOWN SOURCE TYPE in create_landmarker. Aborting.')
        exit(1)

    options = hand_landmarker_options(
        base_options=base_options(model_asset_path=model_path),
        running_mode=running_mode,
        num_hands=1,
        result_callback=callback
    )
    
    return options

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
    print(source_type)
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
    
    # load dicts for drawing
    hierarchy_dict = load_connections('hand_config/hand_connections.json')
    colors_dict = load_colors('hand_config/hand_colors.json', 'hand_config/hand_connections.json')


    # create options for landmarkers 
    options0 = create_options(source_type)
    options1 = create_options(source_type)
    hand_landmarker = mp.tasks.vision.HandLandmarker
    print(options1.running_mode)
    with hand_landmarker.create_from_options(options0) as landmarker0,\
         hand_landmarker.create_from_options(options1) as landmarker1:
        
        # create appropriate detect functions
        detect0 = landmarker0.detect_for_video
        detect1 = landmarker1.detect_for_video
        
        # create return values for stream reading
        ret0 = ret1 = True

        # run while all sources return something
        while ret0 and ret1:

            # time measurements to calculate FPS
            start = time.time()
            
            # Capture frames from all sources
            ret0, frame0 = caps[0].read()
            ret1, frame1 = caps[1].read()

            
            # convert colors
            frame0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGB)
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)

            processed_image0 = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame0)
            processed_image1 = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame1)

            cur_time = int(time.time() * 1000)
            result0 = detect0(processed_image0, cur_time)
            result1 = detect1(processed_image1, cur_time)
            
            if result0 != None:
                draw_detection_result(frame0, result0.hand_landmarks, hierarchy_dict, colors_dict)
                cv2.imshow('frame1', frame0)
  
            if result1 != None:
                draw_detection_result(frame1, result1.hand_landmarks, hierarchy_dict, colors_dict)
                cv2.imshow('frame2', frame1)


            end = time.time()
            print(f'FPS: {1/(end - start)}')
            if cv2.waitKey(int(1/framerate*1000)) == 27:
                break

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows() 

if __name__ == '__main__':
    main()