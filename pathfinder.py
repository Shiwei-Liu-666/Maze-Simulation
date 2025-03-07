# ------ HCARD Group 1 ------
import heapq
from math import atan2, degrees, pi
from Constants import *

class PathFinder:
    """A* pathfinding with turn point detection"""
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self.turn_points = []  # Stores turn point data (index, position, direction)
        self._find_path()
        self._detect_turn_directions()
        
    def _find_path(self):
        start = self.maze.start
        end = self.maze.end
        open_heap = []
        closed = set()
        came_from = {}
        
        g_score = {(r, c): float('inf') for r in range(MAZE_HEIGHT) for c in range(MAZE_WIDTH)}
        f_score = {(r, c): float('inf') for r in range(MAZE_HEIGHT) for c in range(MAZE_WIDTH)}
        
        g_score[start] = 0
        f_score[start] = self._heuristic(start, end)
        
        heapq.heappush(open_heap, (f_score[start], start))
        
        while open_heap:
            current = heapq.heappop(open_heap)[1]
            if current == end:
                self.path = self._reconstruct_path(came_from, current)
                return
                
            closed.add(current)
            for neighbor in self._get_valid_neighbors(current):
                if neighbor in closed:
                    continue
                
                tentative_g = g_score[current] + 1
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
                    heapq.heappush(open_heap, (f_score[neighbor], neighbor))

    def _heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def _get_valid_neighbors(self, pos):
        row, col = pos
        neighbors = []
        if not self.maze.grid[row][col]['top']: neighbors.append((row-1, col))
        if not self.maze.grid[row][col]['bottom']: neighbors.append((row+1, col))
        if not self.maze.grid[row][col]['left']: neighbors.append((row, col-1))
        if not self.maze.grid[row][col]['right']: neighbors.append((row, col+1))
        return neighbors

    def _reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(self.maze.start)
        return path[::-1]
    
    def _detect_turn_directions(self):
        """Turn point detection algorithm"""
        self.turn_points = []
        if len(self.path) < 3:
            return
        
        for i in range(1, len(self.path)-1):
            prev = self.path[i-1]
            current = self.path[i]
            next_ = self.path[i+1]
            
            # Calculate direction vectors (grid coordinates)
            vec_in = (prev[1] - current[1], current[0] - prev[0])    # Rotated 90° for screen coordinates
            vec_out = (next_[1] - current[1], current[0] - next_[0]) 
            
            # Skip straight movements
            if vec_in[0]*vec_out[1] == vec_in[1]*vec_out[0]:  # Check colinearity
                continue
                
            # Calculate angles (considering screen Y-axis points downward)
            angle_in = atan2(-vec_in[1], vec_in[0])  # Invert Y component
            angle_out = atan2(-vec_out[1], vec_out[0])
            diff = (angle_out - angle_in + pi) % (2*pi) - pi
            
            # Valid turn condition: angle change > 10 degrees
            if abs(degrees(diff)) > 10:
                # Determine turn direction
                direction = "Left" if diff > 0 else "Right"  # Adjusted for coordinate rotation
                screen_x = CELL_SIZE * (current[1] + 0.5)
                screen_y = CELL_SIZE * (current[0] + 0.5)
                
                self.turn_points.append({
                    "grid_pos": current,
                    "screen_pos": (screen_x, screen_y),
                    "direction": direction,
                    "angle_diff": abs(degrees(diff))
                })