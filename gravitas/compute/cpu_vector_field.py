
import numpy as np
from typing import Tuple, Union, List, Optional, Any
from ..core.state import state_manager
from ..core.events import Event, EventType, event_bus

class CPUVectorFieldCalculator:
    
    def __init__(self):
        self._event_bus = event_bus
        self._state_manager = state_manager

    def sum_adjacent_vectors(self, grid: np.ndarray, x: int, y: int,
                           self_weight: float = 1.0, neighbor_weight: float = 0.1) -> Tuple[float, float]:
        
        if grid is None:
            return (0.0, 0.0)

        h, w = grid.shape[:2]
        sum_x = 0.0
        sum_y = 0.0

        if 0 <= x < w and 0 <= y < h:
            vx, vy = grid[y, x]
            sum_x += vx * self_weight
            sum_y += vy * self_weight

        neighbors = ((0, -1), (0, 1), (-1, 0), (1, 0))
        for dx, dy in neighbors:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < w and 0 <= ny < h:
                vx, vy = grid[ny, nx]
                sum_x += vx * neighbor_weight
                sum_y += vy * neighbor_weight

        return (sum_x, sum_y)

    def update_grid_with_adjacent_sum(self, grid: np.ndarray) -> np.ndarray:
        
        if grid is None or not isinstance(grid, np.ndarray):
            return grid

        h, w = grid.shape[:2]

        # getconfigparam
        neighbor_weight = self._state_manager.get("vector_neighbor_weight", 0.1)
        self_weight = self._state_manager.get("vector_self_weight", 1.0)

        padded_grid = np.pad(grid, ((1, 1), (1, 1), (0, 0)), mode='edge')

        up_neighbors = padded_grid[2:, 1:-1] * neighbor_weight
        down_neighbors = padded_grid[:-2, 1:-1] * neighbor_weight
        left_neighbors = padded_grid[1:-1, 2:] * neighbor_weight
        right_neighbors = padded_grid[1:-1, :-2] * neighbor_weight

        result = up_neighbors + down_neighbors + left_neighbors + right_neighbors

        result += grid * self_weight

        grid[:] = result
        return grid

    def create_vector_grid(self, width: int = 640, height: int = 480, default: Tuple[float, float] = (0, 0)) -> np.ndarray:
        
        grid = np.zeros((height, width, 2), dtype=np.float32)
        if default != (0, 0):
            grid[:, :, 0] = default[0]
            grid[:, :, 1] = default[1]
        return grid

    def create_tiny_vector(self, grid: np.ndarray, x: float, y: float, mag: float = 1.0) -> None:
        
        if not hasattr(grid, "ndim"):
            return

        h, w = grid.shape[0], grid.shape[1]

        x = max(0.0, min(w - 1.0, float(x)))
        y = max(0.0, min(h - 1.0, float(y)))

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if abs(dx) + abs(dy) == 1:
                    self.add_vector_at_position(grid, x + dx, y + dy, dx * mag, dy * mag)

    def create_tiny_vectors_batch(self, grid: np.ndarray, positions: List[Tuple[float, float, float]]) -> None:
        
        if not hasattr(grid, "ndim") or not positions:
            return

        h, w = grid.shape[0], grid.shape[1]

        for x, y, mag in positions:
            x = max(0.0, min(w - 1.0, float(x)))
            y = max(0.0, min(h - 1.0, float(y)))

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if abs(dx) + abs(dy) == 1:
                        self.add_vector_at_position(grid, x + dx, y + dy, dx * mag, dy * mag)

    def add_vector_at_position(self, grid: np.ndarray, x: float, y: float, vx: float, vy: float) -> None:
        
        if not hasattr(grid, "ndim") or grid.ndim < 3 or grid.shape[2] < 2:
            return

        h, w = grid.shape[0], grid.shape[1]

        x = max(0.0, min(w - 1.0, float(x)))
        y = max(0.0, min(h - 1.0, float(y)))

        x0 = int(np.floor(x))
        x1 = min(x0 + 1, w - 1)
        y0 = int(np.floor(y))
        y1 = min(y0 + 1, h - 1)

        wx = x - x0
        wy = y - y0

        w00 = (1 - wx) * (1 - wy)
        w01 = wx * (1 - wy)
        w10 = (1 - wx) * wy
        w11 = wx * wy

        try:
            grid[y0, x0, 0] += w00 * vx
            grid[y0, x0, 1] += w00 * vy
            grid[y0, x1, 0] += w01 * vx
            grid[y0, x1, 1] += w01 * vy
            grid[y1, x0, 0] += w10 * vx
            grid[y1, x0, 1] += w10 * vy
            grid[y1, x1, 0] += w11 * vx
            grid[y1, x1, 1] += w11 * vy
        except Exception:
            pass

    def fit_vector_at_position(self, grid: np.ndarray, x: float, y: float) -> Tuple[float, float]:
        
        if not hasattr(grid, "ndim") or grid.ndim < 3 or grid.shape[2] < 2:
            return (0.0, 0.0)

        h, w = grid.shape[0], grid.shape[1]

        x = max(0.0, min(w - 1.0, float(x)))
        y = max(0.0, min(h - 1.0, float(y)))

        x0 = int(np.floor(x))
        x1 = min(x0 + 1, w - 1)
        y0 = int(np.floor(y))
        y1 = min(y0 + 1, h - 1)

        v00 = (grid[y0, x0, 0], grid[y0, x0, 1])
        v01 = (grid[y0, x1, 0], grid[y0, x1, 1])
        v10 = (grid[y1, x0, 0], grid[y1, x0, 1])
        v11 = (grid[y1, x1, 0], grid[y1, x1, 1])

        wx = x - x0
        wy = y - y0

        vx = (1 - wx) * (1 - wy) * v00[0] + wx * (1 - wy) * v01[0] + (1 - wx) * wy * v10[0] + wx * wy * v11[0]
        vy = (1 - wx) * (1 - wy) * v00[1] + wx * (1 - wy) * v01[1] + (1 - wx) * wy * v10[1] + wx * wy * v11[1]

        return (vx, vy)

    def fit_vectors_at_positions_batch(self, grid: np.ndarray, positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        
        if not hasattr(grid, "ndim") or grid.ndim < 3 or grid.shape[2] < 2 or not positions:
            return [(0.0, 0.0)] * len(positions)

        return [self.fit_vector_at_position(grid, x, y) for x, y in positions]
