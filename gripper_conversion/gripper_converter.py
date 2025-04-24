import json
import numpy as np

def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

class GripperConverter():
    """
    Used to determine the orientation and position of the end effector.
    """

    def __init__(self, path_to_connections_json):
        # load conections with their names
        with open(path_to_connections_json, 'r') as input_file:
            self.named_connections = json.load(input_file) 
        

    def set_orientation_index_z(self):

        """
        Sets which indexes will be used to determine axes with z-axis going along the index finger.
        """

        # space center is in the first joint of index
        self.center = self.named_connections['fingers']['index'][0]

        # z axis is represented by index finger
        self.z_end = self.named_connections['fingers']['index'][-1]
        
        # x axis is the connection between first joints
        # of index and middle fingers
        self.x_end = self.named_connections['fingers']['middle'][0]
    
    def get_orientation_index_z(self, points3d):
        """
        Returns homogenous orientation of coordinate system with z axis along index finger.
        """

        # get center coordinates
        center = points3d[self.center]

        # get x and z vectors 
        z_vector = points3d[self.z_end] - center
        x_vector = points3d[self.x_end] - center
        
        # calculate y vector. it will be perpendicular to both x and z
        y_vector = np.cross(z_vector, x_vector)

        # normalize y and z
        z_vector = normalize(z_vector)
        y_vector = normalize(y_vector)
        
        # get orthogonal x
        x_vector = np.cross(y_vector, z_vector)

        return [x_vector, y_vector, z_vector], center
