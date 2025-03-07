# Path Planning & IMU Simulation Program for HCARD Group project (***v_0.2***)
This project simulates the navigation process and vibration feedback mechanism of visually impaired users wearing our vibration-based auxiliary navigation tool in an indoor maze environment. The program automatically plans the shortest path from the starting point to the destination based on environmental conditions, then guides the user to reach the target location. At each corner, the system determines the required turning angle using position and orientation data received from the IMU, and transmits vibration commands to the device via the communication module. The code implementation regarding vibration command transmission and actual IMU data acquisition requires further refinement.
## ✨ What's new in ***v_0.2***
1. Logical errors and bugs in corner detection mechanism has been resolved and improved.
2. The multi-level corner detection mechanism has been removed because it is greatly affected by the noise in the IMU data.
3. Improved visualisation. Press `SPACE` to show the path and `BACKSPACE` to show detected corners.
<div style="display: flex; gap: 10px; justify-content: center;">
  <img src="./IMGS/MazeWithoutPath.png" alt="MazeWithoutPathcorner" style="width: 48%;">
  <img src="./IMGS/MazeWithPathTruns.png" alt="MazeWithPathTruns" style="width: 48%;">
</div>
=======
# Path Planning & IMU Simulation Program for HCARD Group project (***v_0.1***)
This project simulates the navigation process and vibration feedback mechanism of visually impaired users wearing our vibration-based auxiliary navigation tool in an indoor maze environment. The program automatically plans the shortest path from the starting point to the destination based on environmental conditions, then guides the user to reach the target location. At each corner, the system determines the required turning angle using position and orientation data received from the IMU, classifies the vibration intensity into three levels based on the absolute angle value, and transmits vibration commands to the device via the communication module. The code implementation regarding vibration command transmission and actual IMU data acquisition requires further refinement.
>>>>>>> 26ce04f0106b07a7de139896f90b9521d2759941

## 📦 Installation
```bash
pip install pygame
pip install numpy
pip install heapq
```
python version: `3.9.0`

## 🚀 Usage
Simply run the `main.py`, and you can change the parameters in the `Constants.py` file.
```bash
python YOUR/PATH/TO/main.py
```
The Maze is saved in `./maze_data/maze.json` file. If you want to change to another maze, just delete it and run the program again, it will generate a new maze and save it in the same path.

## 🗺️ Core Modules

### 🧭 Path Planning Algorithm
The core of the path planning algorithm is the `PathFinder` class, which uses the ***A-Star algorithm*** with some enhancements to find the shortest path.
```python
# Enhanced A* algorithm implementation
class PathFinder:
    """A* pathfinding implementation"""
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self._find_path()
        
    def _find_path(self):
        .......... # core codes
```
#### 🛠️ ***Updates & Improvements & Bug fixing in v_0.2***
Added new turn point detection logic to the `PathFinder`. After the ***A-star algorithm*** plans a shortest path, it directly identifies turn points within this path. The previous implementation incorrectly utilized future-generated IMU data (in simulation), which was a logical error that has now been resolved.
```python
def _detect_turn_directions(self):
        """Turn point detection algorithm"""
        self.turn_points = []
        ....... # core codes
```

### 📡 IMU Data (Simulation)
In this simulation code (`imu.py`), I only simulated the IMU data for now (generating data with Gaussian noise). The real-time IMU data can be obtained by capturing the data from the IMU sensor, and you need to add the code for it in the `get_real_imu_data()` function shown below.
```python
class IMUSimulator:
    def get_simulated_imu(self):
        # Implementation details:
        # 1. Gaussian noise injection: Δx~N(0,σ_x), Δy~N(0,σ_y)
        # 2. Heading calculation: θ = arctan2(Δy, Δx) + N(0,σ_θ)
        # 3. Time synchronization: Controlled by update_interval
        # 4. Motion constraints: Max angular velocity 2rad/s
    def get_real_imu_data(self):
        """REAL IMU data need to be captured by IMU sensor"""
        
        ....... # ADD code for capturing real IMU data
        
        return (x, y, theta)
        pass
```

### ⚡ Vibration feedback
Vibration Feedback is implemented to provide feedback to the user when they make a turn. It uses the `actual_diff` value to determine the turn type and provides appropriate vibration feedback. Send the appropriate vibration feedback via Bluetooth to the device by modifying the `send_vibration_command` function in the `application.py` file:
```python
class MainApplication:
    """Main application controller"""
    .....
    def send_vibration_command(self, level):
        '''send vibration command to the device via Bluetooth'''
        ......  # ADD code for sending this command


        pass
```
#### 🛠️ ***Updates & Improvements & Bug fixing in v_0.2***
Unlike previous versions, the program now triggers the vibration command when the user is 12 pixels away from the next turn. This adjustment accounts for potential Bluetooth communication delays, the duration of vibration feedback, and the user’s required reaction time.
```python
if distance <= self.alert_distance:
   path_angle = atan2(dy, dx)
   agent_angle = self.agent.current_heading
   angle_diff = degrees((path_angle - agent_angle + pi) % (2*pi) - pi)
   
   if abs(angle_diff) < self.direction_alingnment:  # Direction alignment threshold
       print(f"Turn {required_direction} {distance:.1f} units ahead!")
       if not SIMULATION_MODE:
           self.send_vibration_command(required_direction)  # Send vibration command (only used in real environment)
       self.next_turn_index += 1
```

### 🔍 Multi-level Corner Detection
<del>The system implements a three-tier detection mechanism that intelligently identifies turn types by analyzing continuous angular differences (`actual_diff`) along the path.
</del>
#### 🛠️ ***Updates & Improvements & Bug fixing in v_0.2***
This feature has been removed because inherent inaccuracies in the IMU sensor can cause discrepancies between the user's actual orientation and the estimated orientation (compared to an ideal noise-free trajectory, this error ranges from 1 to 12 degrees approximately). In certain scenarios, for example, if the user's actual angle relative to a corner is 55 degrees but the IMU inaccurately estimates it as 62 degrees, the user would receive a `level 2` vibration feedback instead of `level 1`. This mismatch could lead to significant deviation, resulting in navigation failure. Moreover, visually impaired users may even face tripping hazards due to such errors.

### 🎯 Parameters and Constants
The key parameters used in the simulation are defined in the `Constants.py` file, including the maze size, and the parameters for the pygame window and the IMU data (noise and detection interval). The start and end points could be defined in `maze.json`.
```json
"start": [
    0,
    0
  ],
  "end": [
    9,
    14
  ]
```

## ▶️ Demo
![DEMO](IMGS/DemoRecording.gif)

