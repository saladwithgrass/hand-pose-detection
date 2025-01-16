import argparse
import pickle

import sys
sys.path.append('../../')
from utils.general_utils import confirmation_prompt

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('input_file', help='File which image size will be added to.')
    parser.add_argument('-w', '--width', help='Width that will be added to file.', type=int, required=True)
    parser.add_argument('-h', '--height', help='Height that will be added to file.', type=int, required=True)
    parser.add_argument('-H', '--help', action='help', help='show this help message and exit')
    args = parser.parse_args()
    input_filename = args.input_file
    camera_dict = None
    with open(input_filename, 'rb') as input_file:
        camera_dict = pickle.load(input_file)
        
        # if calibration file already has it, ask for confirmation
        if 'image_height' in camera_dict.keys() or 'image_width' in camera_dict.keys():
            # get confirmation from user
            to_write = None
            while to_write is None:
                to_write = confirmation_prompt(f'File {input_filename} already has image size. Are you sure you want to overwrite it?')
            # return if user declined
            if not to_write:
                print('Writing aborted.')
                return

        # add field to dictionary
        camera_dict['image_width'] = args.width
        camera_dict['image_height'] = args.height
    
    print('Writing image size.')
    # reopen file wor write
    with open(input_filename, 'wb') as output_file:
        pickle.dump(camera_dict, output_file)
    


if __name__ == '__main__':
    main()