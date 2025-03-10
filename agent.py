import pygame
from math import cos, sin, pi
from Constants import *


class Agent:
    """Mobile agent with IMU-based navigation"""
    def __init__(self):
        self.trail = []
        # self.current_pos = None
        self.current_pos = (20, 20)
        self.current_heading = 0
        self.last_valid_data = None
    
    def update(self, imu_data):
        """Update position based on IMU data"""
        if imu_data:
            self.last_valid_data = imu_data
            self.current_pos = (imu_data[0], imu_data[1])
            self.current_heading = imu_data[2]
        elif self.last_valid_data:
            # Maintain last known position
            self.current_pos = (self.last_valid_data[0], self.last_valid_data[1])
            self.current_heading = self.last_valid_data[2]
        
        if self.current_pos:
            self.trail.append(self.current_pos)
    
    def draw(self, surface):
        """Render agent and trail"""
        if len(self.trail) >= 2:
            pygame.draw.lines(surface, COLORS['trail'], False, self.trail, 3)
            
        if self.current_pos:
            angle = self.current_heading
            front = (CELL_SIZE/2 * cos(angle), CELL_SIZE/2 * sin(angle))
            left = (CELL_SIZE/4 * cos(angle + pi/2), CELL_SIZE/4 * sin(angle + pi/2))
            right = (CELL_SIZE/4 * cos(angle - pi/2), CELL_SIZE/4 * sin(angle - pi/2))
            points = [
                (self.current_pos[0] + front[0], self.current_pos[1] + front[1]),
                (self.current_pos[0] - front[0]/2 + left[0], self.current_pos[1] - front[1]/2 + left[1]),
                (self.current_pos[0] - front[0]/2 + right[0], self.current_pos[1] - front[1]/2 + right[1])
            ]
            pygame.draw.polygon(surface, COLORS['agent'], points)