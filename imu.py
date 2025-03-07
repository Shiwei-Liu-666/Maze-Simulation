# ------ HCARD Group 1 ------
import numpy as np
from math import sqrt, atan2
from Constants import *

class IMUSimulator:
    """IMU sensor simulator with pre-generated path"""
    def __init__(self, path):
        self.original_path = self._convert_to_screen_coords(path)
        self.interpolated_path = self._interpolate_path()
        self.current_step = 0
        self.last_update_time = 0
        self.history = []
        
    def _convert_to_screen_coords(self, path):
        """Convert grid coordinates to screen coordinates"""
        return [(CELL_SIZE*(c+0.5), CELL_SIZE*(r+0.5)) for (r, c) in path]
    
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
    def get_real_imu_data(self):
        """REAL IMU data need to be captured by IMU sensor"""
        """
        
        


        
        
        """
        # return (x, y, theta) if available, otherwise return None
        pass

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