# ------ HCARD Group 1 ------
import pygame
from maze import MazeGenerator
from pathfinder import PathFinder
from imu import IMUSimulator
from agent import Agent
from math import atan2, degrees, sqrt, cos, sin, pi
from Constants import *


class MainApplication:
    """Main application controller"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.maze = MazeGenerator()
        self.pathfinder = PathFinder(self.maze)
        self.imu = IMUSimulator(self.pathfinder.path)
        self.agent = Agent()
        self.processed_turns = set()
        self.show_path = True
        self.running = True

    def _draw_maze(self):
        """Render maze structure"""
        for row in range(MAZE_HEIGHT):
            for col in range(MAZE_WIDTH):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                if self.maze.grid[row][col]['top']:
                    pygame.draw.line(self.screen, COLORS['wall'], (x, y), (x+CELL_SIZE, y), 3)
                if self.maze.grid[row][col]['left']:
                    pygame.draw.line(self.screen, COLORS['wall'], (x, y), (x, y+CELL_SIZE), 3)
        
        # Draw start and end markers
        pygame.draw.circle(self.screen, COLORS['start'], 
                          (int(CELL_SIZE*0.5), int(CELL_SIZE*0.5)), 8)
        pygame.draw.circle(self.screen, COLORS['end'], 
                          (int(CELL_SIZE*(MAZE_WIDTH-0.5)), int(CELL_SIZE*(MAZE_HEIGHT-0.5))), 8)

    def _draw_path(self):
        """Render planned path"""
        if len(self.pathfinder.path) >= 2:
            points = [(CELL_SIZE*(c+0.5), CELL_SIZE*(r+0.5)) for (r, c) in self.pathfinder.path]
            pygame.draw.lines(self.screen, COLORS['path'], False, points, 5)

    def _detect_turns(self):
        """Detect and process turns"""
        current_step = self.imu.current_step - 1
        if current_step in self.imu.turn_points and current_step not in self.processed_turns:
            self._process_turn(current_step)
    
    def _process_turn(self, step):
        """Calculate and display turn information"""
        p_prev = self.imu.noisy_path[step-1]
        p_current = self.imu.noisy_path[step]
        p_next = self.imu.noisy_path[step+1]
        
        vec_in = (p_current[0]-p_prev[0], p_current[1]-p_prev[1])
        vec_out = (p_next[0]-p_current[0], p_next[1]-p_current[1])
        
        angle_in = atan2(vec_in[1], vec_in[0])
        angle_out = atan2(vec_out[1], vec_out[0])
        diff = degrees((angle_out - angle_in + pi) % (2*pi) - pi)
        
        direction = "Right" if diff > 0 else "Left"
        actual_diff = abs(diff)
        
        if actual_diff <= 60 and actual_diff >= 10:
            level = 1
        elif actual_diff <= 120 and actual_diff >= 61:
            level = 2
        elif actual_diff <= 180 and actual_diff >= 121:
            level = 3
        else:
            level = 0
        
        if level != 0:
            print(f"{direction} turn detected! Level: {level} (Angle: {actual_diff:.1f}°)")
            self.send_vibration_command(level) # Replace with your actual implementation
        self.processed_turns.add(step)

    def send_vibration_command(self, level):
        '''send vibration command to the device via Bluetooth'''
        # ......







        pass

    def run(self):
        """Main application loop"""
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.show_path = not self.show_path
            
            # IMU data handling
            imu_data = self.imu.get_simulated_imu(current_time)  # If in real environment, use get_real_imu_data()
            self.agent.update(imu_data)
            
            # Turn detection
            self._detect_turns()
            
            # Rendering
            self.screen.fill(COLORS['background'])
            self._draw_maze()
            if self.show_path:
                self._draw_path()
            self.agent.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FRAME_RATE)
        
        pygame.quit()