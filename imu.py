# ------ HCARD Group 1 ------
import numpy as np
import socket
import json
from math import sqrt, atan2, radians
from Constants import *

class IMUSimulator:
    """IMU sensor simulator with pre-generated path"""
    def __init__(self, path):
        self.original_path = self._convert_to_screen_coords(path)
        self.interpolated_path = self._interpolate_path()
        self.current_step = 0
        self.last_update_time = 0
        self.history = []
        # UDP socket for receiving IMU data
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('localhost', 65432))
        self.udp_socket.settimeout(0.01)
        
    def _convert_to_screen_coords(self, path):
        """Convert grid coordinates to screen coordinates"""
        return [(CELL_SIZE*(c+0.5), CELL_SIZE*(r+0.5)) for (r, c) in path]
    
    def _convert_real_to_screen(self, real_x, real_y):
        """ 
        Convert real-world grid coordinates to Pygame window pixel coordinates
        
        Coordinate System Definitions:
        - Real-world coordinate system:
        - Maze consists of 15 columns (x-axis: 0-14) and 10 rows (y-axis: 0-9)
        - Origin (0,0) at top-left corner of window (row 0, column 0)
        - x increases to the right (column index: 0 ≤ x < 15)
        - y increases downward (row index: 0 ≤ y < 9)
        - Pygame window coordinate system:
        - Origin (0,0) at top-left corner of window
        - x increases to the right
        - y increases downward
        - Center of each grid cell: (x+0.5)*CELL_SIZE, (y+0.5)*CELL_SIZE
        """
        screen_x = (real_x + 0.5) * CELL_SIZE  # Column index → pixel coordinates (center)
        screen_y = (real_y + 0.5) * CELL_SIZE  # Row index → pixel coordinates (center)
        return screen_x, screen_y

    def _interpolate_path(self):
        """Perform linear interpolation in screen coordinates between start and endpoints"""
        interpolated = []
        if len(self.original_path) < 2:
            return interpolated  # If there are fewer than 2 points in the path

        # Iterate through all adjacent point pairs in the path
        for i in range(len(self.original_path) - 1):
            start_x, start_y = self.original_path[i]    # Get start coordinates
            end_x, end_y = self.original_path[i + 1]    # Get end coordinates

            # Calculate Euclidean distance between points (in pixels)
            dx = end_x - start_x
            dy = end_y - start_y
            distance = sqrt(dx**2 + dy**2)

            # Calculate number of interpolated points based on step size (minimum 1 step)
            step_size_pixels = CELL_SIZE * PATH_INTERPOLATION_STEP
            steps = max(int(distance / step_size_pixels), 1)

            # Generate interpolated points (include start, exclude end)
            for t in np.linspace(0, 1, steps, endpoint=False):
                x = start_x + t * dx
                y = start_y + t * dy
                interpolated.append((x, y))

        # Add the final endpoint
        interpolated.append(self.original_path[-1])
        return interpolated

    def _print_UDP_raw_data(self):  # FOR DEBUG ONLY
        """ print raw data from UDP socket"""
        try:
            raw_data, _ = self.udp_socket.recvfrom(1024)
            try:
                parsed_data = json.loads(raw_data.decode('utf-8'))
                print("[DEBUG] Parsed JSON:", parsed_data)
            except Exception as e:
                print("[DEBUG] JSON parsing failure:", str(e))
        
            return None
            
        except socket.timeout:
            return None
        except Exception as e:
            print("[ERROR] Receive Failure:", str(e))
            return None
        pass

    def get_real_imu_data(self):
        """
        Receive real IMU data via UDP and convert to window coordinates
        Returns: (x_pixel, y_pixel, theta_degrees)
        """
        try:
            # Receive raw data
            raw_data, _ = self.udp_socket.recvfrom(1024)
            data = json.loads(raw_data.decode('utf-8'))
            
            # Extract fields
            real_x = float(data.get('x', 0.0))
            real_y = float(data.get('y', 0.0))
            theta = float(data.get('heading', 0.0))  # Assuming heading is already in window coordinate system
            
            # Coordinate conversion
            screen_x, screen_y = self._convert_real_to_screen(real_x, real_y)
            print("Raw data:", real_x, real_y, theta)
            print("Converted data:", screen_x, screen_y, theta)
            
            # Direction conversion (optional: if real direction needs adjustment)
            # Example: Real 0°=North (up in window coords), Window 0°=right
            # screen_theta = (theta + 90) % 360  # Uncomment if needed
            
            return (screen_x, screen_y, theta)  # Or return (screen_x, screen_y, screen_theta)
            
        except json.JSONDecodeError:
            print("Error: Received data is not valid JSON")
            return None
        except KeyError:
            print("Error: Missing required fields (x/y/heading)")
            return None
        except socket.timeout:
            return None  # Silent return when no data
        except Exception as e:
            print(f"Unknown error: {str(e)}")
            return None

    def get_simulated_imu(self, current_time):
        if self.current_step >= len(self.interpolated_path) or \
        self.current_step >= MAX_IMU_SAMPLES:
            return None
        
        if current_time - self.last_update_time < IMU_INTERVAL:
            return None
        
        # Get interpolated path point
        base_x, base_y = self.interpolated_path[self.current_step]
        
        # Add noise to position
        x = base_x + np.random.normal(0, IMU_NOISE['position'])
        y = base_y + np.random.normal(0, IMU_NOISE['position'])
        
        # Calculate heading based on previous point
        if len(self.history) >= 1:
            prev_x, prev_y, _ = self.history[-1]
            dx = x - prev_x
            dy = y - prev_y
            theta = atan2(dy, dx) + np.random.normal(0, IMU_NOISE['heading'])
        else:
            theta = 0  # Initial heading when no history exists
        
        # Update historical data buffer
        self.history.append((x, y, theta))
        if len(self.history) > 2:
            self.history.pop(0)  # Maintain only the last 2 points
        
        self.last_update_time = current_time
        self.current_step += 1
        return (x, y, theta)