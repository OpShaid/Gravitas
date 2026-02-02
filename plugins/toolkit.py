
import numpy as np

def add_inward_edge_vectors(grid: np.ndarray, magnitude: float = 1.0) -> None:
    
    height, width = grid.shape[:2]

    grid[0, :, 1] += magnitude

    grid[height-1, :, 1] += -magnitude

    grid[:, 0, 0] += magnitude

    grid[:, width-1, 0] += -magnitude
    grid[0, 0] += [magnitude, magnitude]
    grid[0, width-1] += [-magnitude, magnitude]
    grid[height-1, 0] += [magnitude, -magnitude]
    grid[height-1, width-1] += [-magnitude, -magnitude]