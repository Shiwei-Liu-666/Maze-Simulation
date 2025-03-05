# ------ HCARD Group 1 ------
import numpy as np
from math import atan2
from Constants import *

class IMUSimulator:
    """IMU sensor simulator with pre-generated path"""
    def __init__(self, path):
        self.original_path = self._smooth_path(path)
        self.noisy_path = []
        self.turn_points = []
        self._preprocess_path()
        self.current_step = 0
        self.last_update = 0
        
    def _smooth_path(self, path):
        """Convert grid coordinates to screen coordinates"""
        return [(CELL_SIZE*(c+0.5), CELL_SIZE*(r+0.5)) for (r, c) in path]
    
    def _preprocess_path(self):
        """Pre-generate noisy path and detect turns"""
        for i in range(len(self.original_path)):
            x, y = self.original_path[i]
            noisy_x = x + np.random.normal(0, IMU_NOISE['position'])
            noisy_y = y + np.random.normal(0, IMU_NOISE['position'])
            self.noisy_path.append((noisy_x, noisy_y))
            
            if i > 1:
                prev_dir = self._get_direction(self.noisy_path[i-2], self.noisy_path[i-1])
                curr_dir = self._get_direction(self.noisy_path[i-1], self.noisy_path[i])
                if prev_dir != curr_dir:
                    self.turn_points.append(i-1)
    
    def _get_direction(self, p1, p2):
        """Calculate direction vector"""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return (round(dx, 4), round(dy, 4))
    
    def get_real_imu_data(self):
        """REAL IMU data need to be captured by IMU sensor"""
        """
        
        


        
        
        """
        # return (x, y, theta)
        pass
    
    def get_simulated_imu(self, current_time):
        """Get simulated IMU data with timing control"""
        """Do not use this when using real IMU data"""
        if current_time - self.last_update < IMU_INTERVAL:
            return None
            
        if self.current_step >= len(self.noisy_path):
            return None
        
        # Generate data with noise
        x, y = self.noisy_path[self.current_step]
        if self.current_step < len(self.noisy_path)-1:
            dx = self.noisy_path[self.current_step+1][0] - x
            dy = self.noisy_path[self.current_step+1][1] - y
            theta = atan2(dy, dx) + np.random.normal(0, IMU_NOISE['heading'])
        else:
            theta = 0
        
        self.last_update = current_time
        self.current_step += 1
        return (x, y, theta)