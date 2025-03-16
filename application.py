# ------ HCARD Group 1 ------
import pygame
from maze import MazeGenerator
from pathfinder import PathFinder
from imu import IMUSimulator
from agent import Agent
from math import atan2, degrees, sqrt, pi
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
        self.next_turn_index = 0  # Index of next turn point to check
        self.turn_points = self.pathfinder.turn_points
        self.alert_distance = 15  # Advance notification distance (pixels, need to be adjusted in real world).
        self.direction_alingnment = 40
        self.turn_points = self.pathfinder.turn_points
        self.show_turn_points = True

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

    def _draw_turn_markers(self):
        """Draw turn markers on the screen"""
        if not self.show_turn_points:
            return
        
        for turn in self.turn_points:
            x, y = turn["screen_pos"]
            direction = turn["direction"]
            color = COLORS['turn_right'] if direction == "Right" else COLORS['turn_left']
            # Draw circular marker
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 6)
            # Add direction text label
            font = pygame.font.SysFont('Arial', 14)
            text = font.render(direction, True, color)
            self.screen.blit(text, (x + 8, y))

    def send_vibration_command(self, direction):
        '''send vibration command to the device via Bluetooth'''
        # ......







        pass

    def _check_upcoming_turn(self):
        """Check proximity to next turn point"""
        if self.next_turn_index >= len(self.turn_points):
            return
        
        turn_info = self.turn_points[self.next_turn_index]
        turn_x, turn_y = turn_info["screen_pos"]
        required_direction = turn_info["direction"]
        
        agent_x, agent_y = self.agent.current_pos
        dx = turn_x - agent_x
        dy = turn_y - agent_y
        distance = sqrt(dx**2 + dy**2)
        
        if distance <= self.alert_distance:
            path_angle = atan2(dy, dx)
            agent_angle = self.agent.current_heading
            angle_diff = degrees((path_angle - agent_angle + pi) % (2*pi) - pi)
            
            if abs(angle_diff) < self.direction_alingnment:  # Direction alignment threshold
                print(f"Turn {required_direction} {distance:.1f} units ahead!")
                if not SIMULATION_MODE:
                    self.send_vibration_command(required_direction)  # Send vibration command (only used in real environment)
                self.next_turn_index += 1

    def _draw_path_points(self):
        """Draw path points as individual markers"""
        if not hasattr(self, 'show_path_points'):
            self.show_path_points = True
        
        if self.show_path_points:
            point_color = COLORS['path_point']
            point_radius = 4 
            
            for (row, col) in self.pathfinder.path:
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                
                pygame.draw.circle(
                    self.screen,
                    point_color,
                    (int(x), int(y)),
                    point_radius
                )

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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    self.show_turn_points = not self.show_turn_points
            
            # IMU data handling
            if SIMULATION_MODE:  # If in real environment, use get_real_imu_data()
                imu_data = self.imu.get_simulated_imu(current_time)
            else:
                imu_data = self.imu.get_real_imu_data()
            self.agent.update(imu_data)
            
            if DEBUG_MODE:
                # print received UDP rawdata
                self.imu._print_UDP_raw_data()

            # Turns detection
            self._check_upcoming_turn()
            
            # Rendering
            self.screen.fill(COLORS['background'])
            self._draw_maze()
            if self.show_turn_points:
                self._draw_turn_markers()
            if self.show_path:
                self._draw_path()
            self.agent.draw(self.screen)

            if DEBUG_MODE:
                self._draw_path_points()

            pygame.display.flip()
            self.clock.tick(FRAME_RATE)
        
        pygame.quit()
