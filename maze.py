import numpy as np
import json
import os
from Constants import *


class MazeGenerator:
    """Maze generator with file persistence and guaranteed path"""
    def __init__(self):
        self.grid = []
        self.start = (0, 0)
        self.end = (MAZE_HEIGHT-1, MAZE_WIDTH-1)
        
        if not self.load_from_file():
            self.generate_new_maze()
            self.save_to_file()

    def generate_new_maze(self):
        """Generate new maze using Prim's algorithm with path verification"""
        while True:
            self.grid = [[{'top': True, 'bottom': True, 'left': True, 'right': True} 
                        for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
            
            visited = set()
            walls = []
            visited.add(self.start)
            
            for wall in self._get_neighbors(*self.start):
                walls.append((self.start[0], self.start[1], wall))
                
            while walls:
                idx = np.random.randint(0, len(walls))
                row, col, direction = walls.pop(idx)
                nr, nc = self._get_adjacent_cell(row, col, direction)
                
                if (nr, nc) not in visited:
                    self._remove_wall(row, col, nr, nc, direction)
                    visited.add((nr, nc))
                    
                    for wall in self._get_neighbors(nr, nc):
                        walls.append((nr, nc, wall))
            
            if self._path_exists():
                break

    def _path_exists(self):
        """Verify path existence using BFS"""
        visited = set()
        queue = [self.start]
        
        while queue:
            current = queue.pop(0)
            if current == self.end:
                return True
                
            for neighbor in self._get_traversable_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def _get_traversable_neighbors(self, pos):
        """Get accessible neighbors"""
        row, col = pos
        neighbors = []
        if not self.grid[row][col]['top']: neighbors.append((row-1, col))
        if not self.grid[row][col]['bottom']: neighbors.append((row+1, col))
        if not self.grid[row][col]['left']: neighbors.append((row, col-1))
        if not self.grid[row][col]['right']: neighbors.append((row, col+1))
        return neighbors

    def load_from_file(self):
        """Load maze from JSON file"""
        if not os.path.exists(MAZE_FILE):
            return False
            
        try:
            with open(MAZE_FILE, 'r') as f:
                data = json.load(f)
                self.grid = [[{k: bool(v) for k, v in cell.items()} 
                            for cell in row] for row in data['grid']]
                self.start = tuple(data['start'])
                self.end = tuple(data['end'])
                return True
        except Exception as e:
            print(f"Error loading maze: {str(e)}")
            return False

    def save_to_file(self):
        """Save maze to JSON file"""
        os.makedirs(os.path.dirname(MAZE_FILE), exist_ok=True)
        data = {
            'grid': [[{k: int(v) for k, v in cell.items()} 
                    for cell in row] for row in self.grid],
            'start': self.start,
            'end': self.end
        }
        with open(MAZE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_neighbors(self, row, col):
        """Get valid neighbor directions"""
        neighbors = []
        if row > 0: neighbors.append('top')
        if row < MAZE_HEIGHT-1: neighbors.append('bottom')
        if col > 0: neighbors.append('left')
        if col < MAZE_WIDTH-1: neighbors.append('right')
        return neighbors

    def _get_adjacent_cell(self, row, col, direction):
        """Calculate adjacent cell coordinates"""
        if direction == 'top': return (row-1, col)
        if direction == 'bottom': return (row+1, col)
        if direction == 'left': return (row, col-1)
        return (row, col+1)

    def _remove_wall(self, row, col, nr, nc, direction):
        """Remove wall between two cells"""
        if direction == 'top':
            self.grid[row][col]['top'] = False
            self.grid[nr][nc]['bottom'] = False
        elif direction == 'bottom':
            self.grid[row][col]['bottom'] = False
            self.grid[nr][nc]['top'] = False
        elif direction == 'left':
            self.grid[row][col]['left'] = False
            self.grid[nr][nc]['right'] = False
        elif direction == 'right':
            self.grid[row][col]['right'] = False
            self.grid[nr][nc]['left'] = False