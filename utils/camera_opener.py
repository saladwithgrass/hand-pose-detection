import cv2
import json

def create_capture_from_json(dev_id:int, json_path:str) -> cv2.VideoCapture:
    with open(json_path, 'r') as json_input:
        params_dict = json.load(json_input)
    
    cap = cv2.VideoCapture(dev_id, cv2.CAP_V4L2)
    for name, value in params_dict.items():
        # if its fourcc, generate it
        if name == 'CAP_PROP_FOURCC':
            fcc_code = cv2.VideoWriter.fourcc(value[0], value[1], value[2], value[3])
            cap.set(cv2.CAP_PROP_FOURCC, fcc_code)
            continue
        cap.set(getattr(name), value)
    return cap
    