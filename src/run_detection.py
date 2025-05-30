import time
import cv2
import argparse
import sys
from utils.draw_utils import (
    draw_hand_on_image
)
import sys
from detection.capture_detector import CaptureDetector
from threading import Thread


# SECTION FRAME_PROC BEGIN
def run_detector_frame_processing(
        detector:CaptureDetector, 
        detector_id:int, 
        result:list
        ):
    landmarks, result[detector_id] = detector.process_one_frame(return_frame=True)
    draw_hand_on_image(
        result[detector_id],
        landmarks
    )
# SECTION FRAME_PROC END

# SECTION INPUT_SRC_ARG BEGIN
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source_type', 
        help='defines type of input stream: video or camera', 
        choices=('cam', 'vid')
    )
    parser.add_argument(
        'sources', 
        help='list of input sources', 
        nargs='+'
    )
    parser.add_argument(
        '-dev',
        '--by-dev',
        help='Specifies whether cameras sould be identified by their file in /dev',
        required=False,
        action='store_true'
    )
# SECTION INPUT_SRC_ARG END

# SECTION PERF_ARGS BEGIN
    parser.add_argument(
        '-b',
        '--buffer-size',
        help='Specifies buffer size for input streams',
        type=int,
        default=4
    )
    parser.add_argument(
        '-fps',
        '--framerate',
        help='Specifies desired framerate',
        type=int,
        default=30
    )
    args = parser.parse_args()
# SECTION PERF_ARGS END

# SECTION SAVE_ARGS BEGIN
    buffer_size = args.buffer_size
    framerate = args.framerate
    ideal_delta_t_ms = int(1 / framerate * 1000)
# SECTION SAVE_ARGS END

# SECTION OPEN_CAPS BEGIN
    source_type = args.source_type
    caps = list()
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
# SECTION OPEN_CAPS END

# SECTION DETECTION BEGIN
    model_path = 'detection/hand_landmarker.task'

    # create detectors
    detectors = list()
    for cap in caps:
        detectors.append(CaptureDetector(model_path=model_path, capture=cap))
# SECTION DETECTION END

# SECTION CAPTURE_PREP BEGIN
    # create lists for threads 
    threads = [None] * len(detectors)    
    # and for frames
    captured_frames = [None] * len(detectors)
# SECTION CAPTURE_PREP END
    
# SECTION WHILE BEGIN
    # flag for while
    all_ok:bool = True
    while all_ok:

        # get start time for fps
        start_time = time.time() 
# SECTION WHILE END

# SECTION RUN_DETECT BEGIN
        # launch detection on multiple threads for each detector
        for detector_id in range(len(detectors)):
            threads[detector_id] = Thread(
                target=run_detector_frame_processing,
                args=(detectors[detector_id], detector_id, captured_frames)
                )
            threads[detector_id].start()
# SECTION RUN_DETECT END

# SECTION GET_DETECT BEGIN
        # get results for each thread
        for thread in threads:
            thread.join()
# SECTION GET_DETECT END

# SECTION DISPLAY BEGIN
        # show results for each input
        for frame_id in range(len(captured_frames)):
            if len(captured_frames[frame_id]) == 0:
                all_ok = False
            cv2.imshow(f'frame {frame_id}', captured_frames[frame_id])
# SECTION DISPLAY END

# SECTION SYNC BEGIN
        # wait to sync fps
        end_time = time.time()
        real_delta_t_ms = int((end_time - start_time) * 1000)
        cv2.waitKey(
            max(
                ideal_delta_t_ms - real_delta_t_ms,
                1
                ))

        # print FPS 
        end_time = time.time() 
        print(f'FPS: {1 / (end_time - start_time)}')
# SECTION SYNC END

if __name__ == '__main__':
    main()
