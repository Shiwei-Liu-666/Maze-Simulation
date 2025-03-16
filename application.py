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
        pygame.display.set_caption("Maze Navigation System with Vibration Feedback")
        icon = pygame.image.load("./IMGS/icon.png")
        pygame.display.set_icon(icon)
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
        self.alert_distance = 25  # Advance notification distance (pixels, need to be adjusted in real world).
        self.direction_alingnment = 40
        self.turn_points = self.pathfinder.turn_points
        self.show_turn_points = True
        self.current_turn_alert = None
        self.turn_alert_start_time = 0

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

    def _draw_info_panel(self):
        """Draw info panel"""
        panel_y = CELL_SIZE * MAZE_HEIGHT
        font = pygame.font.SysFont('Arial', 24)
        
        # Draw panel background
        pygame.draw.rect(self.screen, COLORS['info_panel_bg'],
                    (0, panel_y, WINDOW_WIDTH, INFO_PANEL_HEIGHT))

        # ===== Table section =====
        # Draw table border
        table_rect = pygame.Rect(20, panel_y + 10, WINDOW_WIDTH-40, 80)
        pygame.draw.rect(self.screen, COLORS['table_border'], table_rect, 2)

        # Draw column divider
        col_x = WINDOW_WIDTH//2
        pygame.draw.line(self.screen, COLORS['table_border'],
                    (col_x, panel_y+10), (col_x, panel_y+90), 2)

        # Draw table headers
        header_font = pygame.font.SysFont('Arial', 20, bold=True)
        header1 = header_font.render("Position", True, COLORS['text'])
        header2 = header_font.render("Heading", True, COLORS['text'])
        self.screen.blit(header1, (col_x//2 - header1.get_width()//2, panel_y+20))
        self.screen.blit(header2, (col_x + col_x//2 - header2.get_width()//2, panel_y+20))

        # Draw values
        x, y = self.agent.current_pos
        theta_deg = degrees(self.agent.current_heading) % 360
        pos_text = font.render(f"({x:.1f}, {y:.1f})", True, COLORS['text'])
        heading_text = font.render(f"{theta_deg:.1f}°", True, COLORS['text'])
        self.screen.blit(pos_text, (col_x//2 - pos_text.get_width()//2, panel_y+50))
        self.screen.blit(heading_text, (col_x + col_x//2 - heading_text.get_width()//2, panel_y+50))

        # ===== Arrow section =====
        arrow_y = panel_y + 100
        arrow_width = ARROW_SIZE  # Triangle base width
        arrow_height = ARROW_SIZE  # Triangle height

        # Left arrow coordinates (pointing left)
        left_arrow = [
            (col_x//2 - arrow_width//2, arrow_y + arrow_height//2),  # Vertex
            (col_x//2 + arrow_width//2, arrow_y),                    # Top right
            (col_x//2 + arrow_width//2, arrow_y + arrow_height)       # Bottom right
        ]

        # Right arrow coordinates (pointing right)
        right_arrow = [
            (col_x + col_x//2 + arrow_width//2, arrow_y + arrow_height//2),  # Vertex
            (col_x + col_x//2 - arrow_width//2, arrow_y),                    # Top left
            (col_x + col_x//2 - arrow_width//2, arrow_y + arrow_height)       # Bottom left
        ]

        # Determine fill colors (keep original logic)
        left_color = COLORS['turn_left'] if (self.current_turn_alert and 
                                        self.current_turn_alert["direction"] == "Left") else None
        right_color = COLORS['turn_right'] if (self.current_turn_alert and 
                                        self.current_turn_alert["direction"] == "Right") else None

        # Draw left arrow (fill first then outline)
        if left_color:
            pygame.draw.polygon(self.screen, left_color, left_arrow)
        pygame.draw.polygon(self.screen, COLORS['arrow_border'], left_arrow, 2)

        # Draw right arrow (fill first then outline)
        if right_color:
            pygame.draw.polygon(self.screen, right_color, right_arrow)
        pygame.draw.polygon(self.screen, COLORS['arrow_border'], right_arrow, 2)

        # ===== Text alert section =====
        if self.current_turn_alert:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.turn_alert_start_time
            
            if elapsed <= 2000:
                direction = self.current_turn_alert["direction"]
                distance = self.current_turn_alert["distance"]
                color = COLORS['turn_right'] if direction == "Right" else COLORS['turn_left']
                alert_text = f"Turn {direction} in {distance:.1f} units!"
                alert_surface = font.render(alert_text, True, color)
                self.screen.blit(alert_surface, (col_x - alert_surface.get_width()//2, arrow_y + ARROW_SIZE + 10))
            else:
                self.current_turn_alert = None

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
                self.current_turn_alert = {
                    "direction": required_direction,
                    "distance": distance
                }
                self.turn_alert_start_time = pygame.time.get_ticks()
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
            self._draw_info_panel()

            if DEBUG_MODE:
                self._draw_path_points()

            pygame.display.flip()
            self.clock.tick(FRAME_RATE)
        
        pygame.quit()
