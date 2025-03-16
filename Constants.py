# ------ HCARD Group 1 ------
SIMULATION_MODE = True
DEBUG_MODE = False
MAZE_WIDTH = 15
MAZE_HEIGHT = 10
INFO_PANEL_HEIGHT = 170
TABLE_ROW_HEIGHT = 40
ARROW_SIZE = 30
MAZE_FILE = "./maze_data/maze_simple.json" # path to the maze file (cam be modified)
CELL_SIZE = 40
WINDOW_WIDTH = CELL_SIZE * MAZE_WIDTH
WINDOW_HEIGHT = CELL_SIZE * MAZE_HEIGHT + INFO_PANEL_HEIGHT  # Window size

# ------FOR SIMULATION ONLY------
IMU_INTERVAL = 100  # 100ms between IMU updates
MAX_IMU_SAMPLES = 500  # samples 500 IMU datas between start and end points
IMU_NOISE = { # IMU noise parameters (Gaussian noise)
    'position': 0.8,
    'heading': 0.01
}
PATH_INTERPOLATION_STEP = 0.1
# -------------------------------

COLORS = {
    'background': (255, 255, 255),
    'wall': (0, 0, 0),
    'start': (0, 255, 0),
    'end': (255, 0, 0),
    'path': (255, 200, 0),
    'agent': (0, 0, 255),
    'trail': (200, 200, 200),
    'turn_right': (255, 153, 51),
    'turn_left': (0, 76, 153),
    'path_point': (100, 100, 255),
    'info_panel_bg': (230, 230, 230),
    'text': (0, 0, 0),
    'table_border': (100, 100, 100),
    'arrow_border': (150, 150, 150),
}
FRAME_RATE = 60