

from typing import List, Dict, Any, Tuple
import numpy as np
from gravitas.compute.vector_field import vector_calculator

class MarkerSystem:
    

    def __init__(self, app_core):
        self.app_core = app_core
        self.vector_calculator = vector_calculator
        self.markers = []

    def add_marker(self, x: float, y: float, mag: float = 1.0, vx: float = 0.0, vy: float = 0.0) -> None:
        
        marker = {"x": float(x), "y": float(y), "mag": float(mag), "vx": float(vx), "vy": float(vy)}
        self.markers.append(marker)
        self._sync_to_state_manager()

    def clear_markers(self) -> None:
        
        self.markers = []
        self._sync_to_state_manager()

    def get_markers(self) -> List[Dict[str, float]]:
        
        return list(self.markers)

    def update_markers(self, grid: np.ndarray, dt: float = 1.0, gravity: float = 0.01, speed_factor: float = 0.9) -> None:
        
        if not self._is_valid_grid(grid):
            return

        self._sync_markers_from_state()

        h, w = grid.shape[0], grid.shape[1]
        cell_size = self.app_core.state_manager.get("cell_size", 1.0)

        marker_positions = self._collect_marker_positions()
        fitted_vectors = self._fit_vectors_batch(grid, marker_positions)

        new_markers = []
        for i, marker in enumerate(self.markers):
            updated_marker = self._update_single_marker(marker, fitted_vectors[i], dt, gravity, speed_factor, cell_size, w, h)
            if updated_marker:
                new_markers.append(updated_marker)

        self._update_markers_list(new_markers)

    def _is_valid_grid(self, grid: np.ndarray) -> bool:
        
        return hasattr(grid, "ndim") and grid.ndim >= 3 and grid.shape[2] >= 2

    def _sync_markers_from_state(self) -> None:
        
        try:
            stored = self.app_core.state_manager.get("markers", None)
            if stored is not None:
                self.markers = list(stored)
        except Exception:
            pass

    def _collect_marker_positions(self) -> List[Tuple[float, float]]:
        
        return [(m["x"], m["y"]) for m in self.markers]

    def _fit_vectors_batch(self, grid: np.ndarray, positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        
        return self.vector_calculator.fit_vectors_at_positions_batch(grid, positions)

    def _update_single_marker(self, marker: Dict[str, float], fitted_vector: Tuple[float, float], dt: float, gravity: float, speed_factor: float, cell_size: float, w: int, h: int) -> Dict[str, float]:
        
        x, y, mag, vx, vy = marker["x"], marker["y"], marker["mag"], marker["vx"], marker["vy"]
        try:
            fitted_vx, fitted_vy = fitted_vector

            # updatevelocity
            vx += fitted_vx / mag
            vy += fitted_vy / mag

            # clampvelocity
            vx, vy = self._clamp_velocity(vx, vy, cell_size)

            # updateposition
            x, y = self._update_position(x, y, vx, vy, dt, w, h)

            vx, vy = self._apply_physics(vx, vy, gravity, speed_factor, dt)

            marker["x"], marker["y"], marker["vx"], marker["vy"] = x, y, vx, vy
            return marker
        except Exception as e:
            print(f"Error updating marker at ({x}, {y}): {str(e)}")
            return marker

    def _clamp_velocity(self, vx: float, vy: float, cell_size: float) -> Tuple[float, float]:
        
        speed = (vx ** 2 + vy ** 2) ** 0.5
        if speed > cell_size:
            vx = vx / speed * cell_size
            vy = vy / speed * cell_size
        return vx, vy

    def _update_position(self, x: float, y: float, vx: float, vy: float, dt: float, w: int, h: int) -> Tuple[float, float]:
        
        new_x = max(0.0, min(w - 1.0, x + vx * dt))
        new_y = max(0.0, min(h - 1.0, y + vy * dt))
        return new_x, new_y

    def _apply_physics(self, vx: float, vy: float, gravity: float, speed_factor: float, dt: float) -> Tuple[float, float]:
        
        vy += gravity * dt
        vx *= speed_factor
        vy *= speed_factor
        return vx, vy

    def _update_markers_list(self, new_markers: List[Dict[str, float]]) -> None:
        
        self.markers = new_markers
        self._sync_to_state_manager()

    def create_tiny_vector(self, grid: np.ndarray, x: float, y: float, mag: float = 1.0) -> None:
        self.vector_calculator.create_tiny_vector(grid, x, y, mag)

    def add_vector_at_position(self, grid: np.ndarray, x: float, y: float, vx: float, vy: float) -> None:
        self.vector_calculator.add_vector_at_position(grid, x, y, vx, vy)
        

    def fit_vector_at_position(self, grid: np.ndarray, x: float, y: float) -> Tuple[float, float]:
        return self.vector_calculator.fit_vector_at_position(grid, x, y)

    def update_field_and_markers(self, grid: np.ndarray, dt: float, gravity: float, speed_factor: float) -> None:
        self.batch_create_tiny_vectors_from_markers(grid, self.markers)
        self.update_markers(grid, dt=dt, gravity=gravity, speed_factor=speed_factor)

    def batch_create_tiny_vectors_from_markers(self, grid: np.ndarray, markers: List[Dict[str, float]]) -> None:
        
        tiny_vector_positions = [(m["x"], m["y"], m["mag"]) for m in markers]
        if tiny_vector_positions:
            self.vector_calculator.create_tiny_vectors_batch(grid, tiny_vector_positions)

    def _sync_to_state_manager(self) -> None:
        
        try:
            self.app_core.state_manager.set("markers", list(self.markers))
        except Exception:
            pass

