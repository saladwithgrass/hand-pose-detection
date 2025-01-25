import json

class GripperConverter():
    """
    Used to determine the orientation and position of the end effector.
    """

    def __init__(self, path_to_connections_json):
        # load conections with their names
        with open(path_to_connections_json, 'r') as input_file:
            named_connections = json.load(input_file) 
        

    def set_orientation_index_z(self, named_connections):
        """
        Sets which indexes will be used to determine axes.
        """

        # space center is in the first joint of index
        self.center = named_connections['fingers']['index'][0]

        # z axis is represented by index finger
        self.z_indexes = [named_connections['fingers']['index'][0], named_connections['fingers']['index'][-1]]
        
        # x axis is the connection between first joints
        # of index and middle fingers
        self.x_indexes = [named_connections['fingers']['index'][0], named_connections['fingers']['middle'][0]]
    
    def get_orientation_index_z(self, points3d):
        #
        pass