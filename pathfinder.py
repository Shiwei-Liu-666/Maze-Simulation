# ------ HCARD Group 1 ------
import heapq
from Constants import *

class PathFinder:
    """A* pathfinding implementation"""
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self._find_path()
        
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