import numpy as np
from gripper_conversion.gripper_converter_interface import GripperConverterInterface, normalize

class BasicGripperConverter(GripperConverterInterface):
    def __init__(self, path_to_connections_json):
        super().__init__(path_to_connections_json)

        self.index_end_idx = self.named_connections['fingers']['index'][-1]
        self.index_start_idx = self.named_connections['fingers']['index'][0]
        self.thumb_end_idx = self.named_connections['fingers']['thumb'][-1]
        self.thumb_start_idx = self.named_connections['fingers']['thumb'][1]

    def get_gripper_state(self, points3d):
        thumb_start_pos = points3d[self.thumb_start_idx]
        index_start_pos = points3d[self.index_start_idx]
        center = (thumb_start_pos + index_start_pos) / 2

        thumb_end_pos = points3d[self.thumb_end_idx]
        index_end_pos = points3d[self.index_end_idx]
        gripping_center = (thumb_end_pos + index_end_pos) / 2

        distance = float(np.linalg.norm(thumb_end_pos - index_end_pos))

        index_vector = index_end_pos - center
        thumb_vector = thumb_end_pos - center

        # x axis is perpendicular to the plane of gripper
        x_axis = normalize(np.cross(index_vector, thumb_vector))
        # z axis is from midpoint between thumb and index start 
        # to the midpoint between their ends
        z_axis = normalize(gripping_center - center)
        # y axis is a cross product of x and z
        y_axis = normalize(np.cross(z_axis, x_axis))

        return [x_axis, y_axis, z_axis], gripping_center, distance
        

