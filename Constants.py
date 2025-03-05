# ------ HCARD Group 1 ------
MAZE_WIDTH = 15
MAZE_HEIGHT = 10
MAZE_FILE = "./maze_data/maze.json" # path to the maze file (cam be modified)
CELL_SIZE = 40
IMU_NOISE = { # IMU noise parameters (for SIMULATION ONLY)
    'position': 2.5,
    'heading': 0.25
}
WINDOW_WIDTH = CELL_SIZE * MAZE_WIDTH
WINDOW_HEIGHT = CELL_SIZE * MAZE_HEIGHT # Window size
IMU_INTERVAL = 500  # 500ms between IMU updates (for SIMULATION ONLY)
COLORS = {
    'background': (255, 255, 255),
    'wall': (0, 0, 0),
    'start': (0, 255, 0),
    'end': (255, 0, 0),
    'path': (255, 200, 0),
    'agent': (0, 0, 255),
    'trail': (200, 200, 200)
}
FRAME_RATE = 60