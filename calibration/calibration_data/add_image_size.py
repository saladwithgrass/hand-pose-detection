import argparse
import pickle

import sys
sys.path.append('../../')
from utils.confirmation import confirmation_prompt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='File which image size will be added to.')
    parser.add_argument('width', help='Width that will be added to file.', type=int)
    parser.add_argument('height', help='Height that will be added to file.', type=int)
    args = parser.parse_args()
    input_filename = args.input_file
    camera_dict = None
    with open(input_filename, 'rb') as input_file:
        camera_dict = pickle.load(input_file)
        
        # if calibration file already has it, ask for confirmation
        if 'image_size' in camera_dict.keys():
            # get confirmation from user
            to_write = None
            while to_write is None:
                to_write = confirmation_prompt(f'File {input_filename} already has image_size. Are you sure you want to overwrite it?')
            # return if user declined
            if not to_write:
                return

        # add field to dictionary
        camera_dict['image_size'] = (args.height, args.width)
    
    # reopen file wor write
    with open(input_filename, 'wb') as output_file:
        pickle.dump(camera_dict)
    


if __name__ == '__main__':
    main()