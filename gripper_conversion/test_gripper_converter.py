import json
from sys import last_traceback
import numpy as np
from gripper_conversion.gripper_converter_interface import normalize, GripperConverterInterface

# SECTION INIT BEGIN
class TestGripperConverter(GripperConverterInterface):
    """
    Used to determine the orientation and position of the end effector.
    """

    def __init__(self, path_to_connections_json):
        super().__init__(path_to_connections_json)

        self.set_orientation_index_z()
# SECTION INIT END
        

# SECTION SET_PARAMS BEGIN
    def set_orientation_index_z(self):

        """
        Sets which indexes will be used to determine axes with z-axis going along the index finger.
        """

        # origin is in the first joint of index
        self.center = self.named_connections['fingers']['index'][0]

        # z axis is represented by index finger
        self.z_end = self.named_connections['fingers']['index'][-1]
        
        # x axis is the connection between first joints
        # of index and middle fingers
        self.x_end = self.named_connections['fingers']['middle'][0]
# SECTION SET_PARAMS END
    

# SECTION CENTER BEGIN
    def get_gripper_state(self, points3d):
        """
        Returns homogenous orientation of coordinate system with z axis along index finger.
        """

        # get center coordinates
        center = points3d[self.center]
# SECTION CENTER END

# SECTION VECTORS BEGIN
        # get x and z vectors 
        z_vector = points3d[self.z_end] - center
        x_vector = points3d[self.x_end] - center
# SECTION VECTORS END
        
# SECTION YCALC BEGIN
        # calculate y vector. it will be perpendicular to both x and z
        y_vector = np.cross(z_vector, x_vector)
# SECTION YCALC END

# SECTION NORMALIZE BEGIN
        # normalize y and z
        z_vector = normalize(z_vector)
        y_vector = normalize(y_vector)
# SECTION NORMALIZE END
        
# SECTION ORTHO BEGIN
        # get orthogonal x
        x_vector = np.cross(y_vector, z_vector)

        return [x_vector, y_vector, z_vector], center, 0
# SECTION ORTHO END

