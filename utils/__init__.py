from utils import draw_utils
print('Utils Module Imported')

connections_dict, colors_dict = draw_utils.load_colors_and_connections(
    'config/hand_colors.json', 
    'config/hand_connections.json'
)
