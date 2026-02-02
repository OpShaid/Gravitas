
import numpy as np
from typing import Tuple, Union, List, Optional, Any
from ..core.config import config_manager
from ..core.events import Event, EventType, event_bus, EventHandler
from ..core.state import state_manager
from .cpu_vector_field import CPUVectorFieldCalculator
from .gpu_vector_field import GPUVectorFieldCalculator

class VectorFieldCalculator(EventHandler):
    
    def __init__(self):
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._config_manager = config_manager

        self._cpu_calculator = CPUVectorFieldCalculator()
        self._gpu_calculator = None

        try:
            self._gpu_calculator = GPUVectorFieldCalculator()
            print("[vector fieldcompute] GPUcomputeinitializesuccess")
        except Exception as e:
            print(f"[vector fieldcompute] GPUcomputeinitializefail: {e}")

        self._current_device = self._config_manager.get("compute_device", "cpu")

        # subscribeevent
        self._event_bus.subscribe(EventType.APP_INITIALIZED, self)
        self._event_bus.subscribe(EventType.CONFIG_CHANGED, self)

    @property
    def current_device(self) -> str:
        
        return self._current_device

    def set_device(self, device: str) -> bool:
        
        if device not in ["cpu", "gpu"]:
            return False

        if device == "gpu" and self._gpu_calculator is None:
            print("[vector fieldcompute] GPUcomputeunavailable")
            return False

        self._current_device = device
        self._config_manager.set("compute_device", device)

        self._event_bus.publish(Event(
            EventType.APP_INITIALIZED,
            {"device": device},
            "VectorFieldCalculator"
        ))

        return True

    def sum_adjacent_vectors(self, grid: np.ndarray, x: int, y: int) -> Tuple[float, float]:
        
        self_weight = self._config_manager.get("vector_self_weight", 0.2)
        neighbor_weight = self._config_manager.get("vector_neighbor_weight", 0.2)

        if grid is None:
            return (0.0, 0.0)

        if not isinstance(grid, np.ndarray):
            raise TypeError("grid mustis numpy.ndarray type")

        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        return calculator.sum_adjacent_vectors(
            grid, x, y, self_weight, neighbor_weight
        )

    def update_grid_with_adjacent_sum(self, grid: np.ndarray) -> np.ndarray:
        
        if grid is None or not isinstance(grid, np.ndarray):
            return grid

        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        return calculator.update_grid_with_adjacent_sum(grid)

    def create_vector_grid(self, width: int = 640, height: int = 480, default: Tuple[float, float] = (0, 0)) -> np.ndarray:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        return calculator.create_vector_grid(width, height, default)

    def create_tiny_vector(self, grid: np.ndarray, x: float, y: float, mag: float = 1.0) -> None:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        calculator.create_tiny_vector(grid, x, y, mag)

    def create_tiny_vectors_batch(self, grid: np.ndarray, positions: List[Tuple[float, float, float]]) -> None:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        if hasattr(calculator, 'create_tiny_vectors_batch'):
            calculator.create_tiny_vectors_batch(grid, positions)
        else:
            for x, y, mag in positions:
                calculator.create_tiny_vector(grid, x, y, mag)

    def add_vector_at_position(self, grid: np.ndarray, x: float, y: float, vx: float, vy: float) -> None:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        calculator.add_vector_at_position(grid, x, y, vx, vy)

    def fit_vector_at_position(self, grid: np.ndarray, x: float, y: float) -> Tuple[float, float]:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        return calculator.fit_vector_at_position(grid, x, y)

    def fit_vectors_at_positions_batch(self, grid: np.ndarray, positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        
        calculator = self._gpu_calculator if self._current_device == "gpu" and self._gpu_calculator else self._cpu_calculator

        if hasattr(calculator, 'fit_vectors_at_positions_batch'):
            return calculator.fit_vectors_at_positions_batch(grid, positions)
        else:
            return [calculator.fit_vector_at_position(grid, x, y) for x, y in positions]

    def handle(self, event: Event) -> None:
        
        if event.type == EventType.APP_INITIALIZED:
            if "device" in event.data:
                self.set_device(event.data["device"])
        elif event.type == EventType.CONFIG_CHANGED:
            data = event.data or {}
            key = data.get("key")
            if key == "compute_device":
                new_device = data.get("new_value")
                if new_device and new_device != self._current_device:
                    if new_device == "gpu" and self._gpu_calculator is None:
                        print("[vector fieldcompute] GPUcomputeunavailable (config)")
                    else:
                        self._current_device = new_device
                        print(f"[vector fieldcompute] computedevicetoggleas: {new_device} (config)")

    def cleanup(self) -> None:
        
        if self._gpu_calculator:
            self._gpu_calculator.cleanup()

vector_calculator = VectorFieldCalculator()

def sum_adjacent_vectors(grid: np.ndarray, x: int, y: int) -> Tuple[float, float]:
    
    return vector_calculator.sum_adjacent_vectors(grid, x, y)

def update_grid_with_adjacent_sum(grid: np.ndarray) -> np.ndarray:
    
    return vector_calculator.update_grid_with_adjacent_sum(grid)

def create_vector_grid(width: int = 640, height: int = 480, default: Tuple[float, float] = (0, 0)) -> np.ndarray:
    
    return vector_calculator.create_vector_grid(width, height, default)
