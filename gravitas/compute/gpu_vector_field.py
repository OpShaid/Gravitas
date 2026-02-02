
import numpy as np
import pyopencl as cl
from typing import Tuple, Union, List, Optional, Any
from ..core.state import state_manager
from ..core.events import Event, EventType, event_bus

class GPUVectorFieldCalculator:
    
    def __init__(self):
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._ctx = None
        self._queue = None
        self._programs = {}
        self._kernels = {}
        self._initialized = False

        # initializeOpenCL
        self._init_opencl()

    def _init_opencl(self) -> None:
        
        try:
            platforms = cl.get_platforms()
            if not platforms:
                raise RuntimeError("not foundOpenCLplatform")

            platform = platforms[0]
            devices = platform.get_devices(cl.device_type.GPU)

            if not devices:
                devices = platform.get_devices(cl.device_type.CPU)
                if not devices:
                    raise RuntimeError("not foundavailableOpenCLdevice")

            self._ctx = cl.Context(devices)
            self._queue = cl.CommandQueue(self._ctx)

            self._compile_programs()

            self._initialized = True
            print("[GPUcompute] OpenCLinitializesuccess")

            self._event_bus.publish(Event(
                EventType.GPU_COMPUTE_STARTED,
                {"device": "gpu", "status": "initialized"},
                "GPUVectorFieldCalculator"
            ))
        except Exception as e:
            print(f"[GPUcompute] OpenCLinitializefail: {e}")
            self._initialized = False

            self._event_bus.publish(Event(
                EventType.GPU_COMPUTE_ERROR,
                {"device": "gpu", "status": "failed", "error": str(e)},
                "GPUVectorFieldCalculator"
            ))

    def _compile_programs(self) -> None:
        
        sum_adjacent_kernel = 

        update_grid_kernel = 

        create_tiny_vectors_batch_kernel = 

        fit_vectors_at_positions_batch_kernel = 

        try:
            self._programs['sum_adjacent_vectors'] = cl.Program(self._ctx, sum_adjacent_kernel).build()
            self._programs['update_grid_with_adjacent_sum'] = cl.Program(self._ctx, update_grid_kernel).build()
            self._programs['create_tiny_vectors_batch'] = cl.Program(self._ctx, create_tiny_vectors_batch_kernel).build()
            self._programs['fit_vectors_at_positions_batch'] = cl.Program(self._ctx, fit_vectors_at_positions_batch_kernel).build()

            self._kernels['sum_adjacent_vectors'] = cl.Kernel(self._programs['sum_adjacent_vectors'], 'sum_adjacent_vectors')
            self._kernels['update_grid_with_adjacent_sum'] = cl.Kernel(self._programs['update_grid_with_adjacent_sum'], 'update_grid_with_adjacent_sum')
            self._kernels['create_tiny_vectors_batch'] = cl.Kernel(self._programs['create_tiny_vectors_batch'], 'create_tiny_vectors_batch_kernel')
            self._kernels['fit_vectors_at_positions_batch'] = cl.Kernel(self._programs['fit_vectors_at_positions_batch'], 'fit_vectors_at_positions_batch_kernel')
        except Exception as e:
            print(f"[GPUcompute] OpenCLprogramcompilefail: {e}")
            raise

    def sum_adjacent_vectors(self, grid: np.ndarray, x: int, y: int,
                           self_weight: float = 1.0, neighbor_weight: float = 0.1) -> Tuple[float, float]:
        
        if not self._initialized:
            raise RuntimeError("GPUcomputeinitialize")

        if grid is None:
            return (0.0, 0.0)

        if not isinstance(grid, np.ndarray):
            raise TypeError("grid mustis numpy.ndarray type")

        h, w = grid.shape[:2]

        result = np.zeros((h, w, 2), dtype=np.float32)

        grid_buf = cl.Buffer(self._ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=grid)
        result_buf = cl.Buffer(self._ctx, cl.mem_flags.WRITE_ONLY, result.nbytes)

        self._kernels['sum_adjacent_vectors'].set_args(
            grid_buf, result_buf,
            np.int32(w), np.int32(h), np.int32(x), np.int32(y),
            np.float32(self_weight), np.float32(neighbor_weight)
        )
        cl.enqueue_nd_range_kernel(self._queue, self._kernels['sum_adjacent_vectors'], (w, h), None)

        cl.enqueue_copy(self._queue, result, result_buf)

        return (result[y, x, 0], result[y, x, 1])

    def update_grid_with_adjacent_sum(self, grid: np.ndarray) -> np.ndarray:
        
        if not self._initialized:
            raise RuntimeError("GPUcomputeinitialize")

        if grid is None or not isinstance(grid, np.ndarray):
            return grid

        h, w = grid.shape[:2]

        # getconfigparam
        neighbor_weight = self._state_manager.get("vector_neighbor_weight", 0.1)
        self_weight = self._state_manager.get("vector_self_weight", 1.0)

        grid_buf = cl.Buffer(self._ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=grid)

        self._kernels['update_grid_with_adjacent_sum'].set_args(
            grid_buf, np.int32(w), np.int32(h),
            np.float32(self_weight), np.float32(neighbor_weight)
        )
        cl.enqueue_nd_range_kernel(self._queue, self._kernels['update_grid_with_adjacent_sum'], (w, h), None)

        cl.enqueue_copy(self._queue, grid, grid_buf)

        return grid

    def create_vector_grid(self, width: int = 640, height: int = 480, default: Tuple[float, float] = (0, 0)) -> np.ndarray:
        
        grid = np.zeros((height, width, 2), dtype=np.float32)
        if default != (0, 0):
            grid[:, :, 0] = default[0]
            grid[:, :, 1] = default[1]
        return grid

    def create_tiny_vector(self, grid: np.ndarray, x: float, y: float, mag: float = 1.0) -> None:
        
        if not self._initialized:
            return

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
        
        if not self._initialized:
            raise RuntimeError("GPUcomputeinitialize")

        if not hasattr(grid, "ndim") or not positions:
            return

        h, w = grid.shape[0], grid.shape[1]
        num_positions = len(positions)

        positions_array = np.array(positions, dtype=np.float32).flatten()

        temp_grid_flat = np.zeros((h * w * 2,), dtype=np.float32)

        temp_grid_buf = cl.Buffer(self._ctx, cl.mem_flags.WRITE_ONLY, temp_grid_flat.nbytes)
        positions_buf = cl.Buffer(self._ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=positions_array)

        self._kernels['create_tiny_vectors_batch'].set_args(
            temp_grid_buf, positions_buf,
            np.int32(w), np.int32(h), np.int32(num_positions)
        )
        cl.enqueue_nd_range_kernel(self._queue, self._kernels['create_tiny_vectors_batch'], (num_positions,), None)

        cl.enqueue_copy(self._queue, temp_grid_flat, temp_grid_buf)

        temp_grid = temp_grid_flat.reshape((h, w, 2))
        grid += temp_grid

    def add_vector_at_position(self, grid: np.ndarray, x: float, y: float, vx: float, vy: float) -> None:
        
        if not self._initialized:
            return

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
        
        if not self._initialized:
            raise RuntimeError("GPUcomputeinitialize")

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
        
        if not self._initialized:
            raise RuntimeError("GPUcomputeinitialize")

        if not hasattr(grid, "ndim") or grid.ndim < 3 or grid.shape[2] < 2 or not positions:
            return [(0.0, 0.0)] * len(positions)

        h, w = grid.shape[0], grid.shape[1]
        num_positions = len(positions)

        positions_array = np.array(positions, dtype=np.float32).flatten()

        results = np.zeros((num_positions, 2), dtype=np.float32)

        grid_buf = cl.Buffer(self._ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=grid)
        positions_buf = cl.Buffer(self._ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=positions_array)
        results_buf = cl.Buffer(self._ctx, cl.mem_flags.WRITE_ONLY, results.nbytes)

        self._kernels['fit_vectors_at_positions_batch'].set_args(
            grid_buf, positions_buf, results_buf,
            np.int32(w), np.int32(h), np.int32(num_positions)
        )
        cl.enqueue_nd_range_kernel(self._queue, self._kernels['fit_vectors_at_positions_batch'], (num_positions,), None)

        cl.enqueue_copy(self._queue, results, results_buf)

        return [(results[i, 0], results[i, 1]) for i in range(num_positions)]

    def cleanup(self) -> None:
        
        if self._ctx:
            del self._ctx
        if self._queue:
            del self._queue
        self._programs.clear()
        self._kernels.clear()
        self._initialized = False
