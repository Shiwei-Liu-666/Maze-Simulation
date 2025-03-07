# ------ HCARD Group 1 ------
SIMULATION_MODE = True
MAZE_WIDTH = 15
MAZE_HEIGHT = 10
MAZE_FILE = "./maze_data/maze.json" # path to the maze file (cam be modified)
CELL_SIZE = 40
WINDOW_WIDTH = CELL_SIZE * MAZE_WIDTH
WINDOW_HEIGHT = CELL_SIZE * MAZE_HEIGHT # Window size

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
}
FRAME_RATE = 60