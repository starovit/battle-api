import numpy as np
import scipy.ndimage
import random

class MapCreator():
    
    def __init__(self, size):
        self.size = size

    def create_mine_map(self,
                        left_bottom_corner =(0,0),
                        right_top_corner=(0,0),
                        num_mines=1):
        
        mine_map = {}
        for x in range(left_bottom_corner[0], right_top_corner[0]):
            for y in range(left_bottom_corner[1], right_top_corner[1]):
                mine_map[(x,y)] = random.randint(0, num_mines)
        
        self.mine_map = mine_map
        return mine_map.copy()

    def create_height_map(self, case="random"):
        if case == "random":
            size = self.size
            height_map = np.random.rand(size, size)
            num_mountains = random.randint(10, 30)
            for _ in range(num_mountains):
                # Choose a random position for the mountain
                x, y = np.random.randint(0, size, 2)
                # Create a mountain by increasing the height at the chosen position
                height_map[x:x+12, y:y+12] += 0.5
            # Smooth the height matrix
            height_map = scipy.ndimage.gaussian_filter(height_map,
                                                       sigma=3)
            
            height_map = (height_map-height_map.min())/(height_map.max() - height_map.min())
        
        self.height_map = height_map
        return height_map
    
    def save_heights(self, path_to_file="database/heights.txt"):
        np.savetxt(path_to_file, self.height_map)

    def read_heights(self, path_to_file="database/heights.txt"):
        self.height_map = np.loadtxt(path_to_file)