import json
import numpy as np

def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

class DummyGripperConverter():
    """
    Used to determine the orientation and position of the end effector.
    """

    def __init__(self, path_to_connections_json):
        # load conections with their names
        with open(path_to_connections_json, 'r') as input_file:
            self.named_connections = json.load(input_file) 

    def get_gripper_state(self, points3d):
        """
        Args:
            points3d:np.ndarray - an array of points in order specified in input json file
        Returns:
            axes:tuple[np.ndarray, np.ndarray, np.ndarray] - an array of three
            vectors: XYZ axes of the end-effector.
            
            translation:np.ndarray - a vector representing the position of the end-effector.

            grip:float - distance between gripper's fingers
        """
        return None, None, None
