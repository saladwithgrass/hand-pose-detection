from utils import draw_utils
print('Utils Module Imported')
connection_dict = draw_utils.load_connections('config/hand_connections.json')
colors_dict = draw_utils.load_colors('config/hand_colors.json', 'config/hand_connections.json')
