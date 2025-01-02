import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import argparse
from utils.draw_results import load_connections, load_colors, draw_detection_result, draw_hand_landmarks_on_live
import numpy as np
import sys
from capture_detector import CaptureDetector
from threading import Thread

def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def run_detector_frame_processing(
        detector:CaptureDetector, 
        detector_id:int, 
        result:list
        ):
    result[detector_id] = detector.process_one_frame()

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

    model_path = 'hand_landmarker.task'

    # create detectors
    detectors = list()
    for cap in caps:
        detectors.append(CaptureDetector(model_path=model_path, capture=cap))

    threads = [None] * len(detectors)    
    frames = [None] * len(detectors)
    all_ok:bool = True
    while all_ok:
        start_time = time.time() 
        for detector_id in range(len(detectors)):
            threads[detector_id] = Thread(
                target=run_detector_frame_processing,
                args=(detectors[detector_id], detector_id, frames)
                )
            threads[detector_id].start()

        for thread in threads:
            thread.join()
    
        for frame_id in range(len(frames)):
            if frames[frame_id] == []:
                all_ok = False
            cv2.imshow(f'frame {frame_id}', frames[frame_id])
        cv2.waitKey(int(1 /framerate * 1000))    
        
        end_time = time.time() 
        print(f'FPS: {1 / (end_time - start_time)}')

if __name__ == '__main__':
    main()