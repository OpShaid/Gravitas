# Application core module - main app functionality
import os
import threading
import numpy as np
import time
from typing import Optional, Dict, Any, Tuple, Callable, Union
from .events import Event, EventType, event_bus, EventHandler, EventBus
from .state import StateManager, state_manager
from .config import ConfigManager, config_manager
from .container import container
from ..compute.vector_field import VectorFieldCalculator
from ..graphics.renderer import VectorFieldRenderer
from ..window.window import Window

class FPSLimiter(EventHandler):
    def __init__(self, state_manager: StateManager, event_bus: EventBus, config_manager: ConfigManager):
        self._state_manager = state_manager
        self._event_bus = event_bus
        self._config_manager = config_manager
        self._last_time = time.time()
        self._enabled = True

        # subscribe to config changes
        self._event_bus.subscribe(EventType.CONFIG_CHANGED, self)

    def limit_fps(self) -> None:
        if not self._enabled:
            return

        target_fps = self._config_manager.get("target_fps", 60)
        if target_fps <= 0:
            return

        frame_time = 1.0 / target_fps
        current_time = time.time()
        elapsed = current_time - self._last_time

        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)

        self._last_time = time.time()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def handle(self, event: Event) -> None:
        if event.type == EventType.CONFIG_CHANGED and event.data.get("key") == "target_fps":
            # reset timer on config change
            self._last_time = time.time()

class GridManager(EventHandler):
    def __init__(self, state_manager: StateManager, event_bus: "EventBus"):
        self._state_manager = state_manager
        self._event_bus = event_bus
        self._lock = threading.RLock()
        self._grid = None

        # init grid state
        self._state_manager.set("grid_width", 640)
        self._state_manager.set("grid_height", 480)
        self._state_manager.set("grid_updated", False)

        # subscribe events
        self._event_bus.subscribe(EventType.CLEAR_GRID, self)
        self._event_bus.subscribe(EventType.TOGGLE_GRID, self)

    @property
    def grid(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._grid.copy() if self._grid is not None else None

    def init_grid(self, width: int = 640, height: int = 480, default: Tuple[float, float] = (0.0, 0.0)) -> np.ndarray:
        with self._lock:
            self._grid = np.zeros((height, width, 2), dtype=np.float32)
            if default != (0.0, 0.0):
                self._grid[:, :, 0] = default[0]
                self._grid[:, :, 1] = default[1]

            # update state
            self._state_manager.update({
                "grid_width": width,
                "grid_height": height,
                "grid_updated": True
            })

            # publish event
            self._event_bus.publish(Event(
                EventType.GRID_UPDATED,
                {"width": width, "height": height},
                "GridManager"
            ))

            return self._grid.copy()

    def update_grid(self, updates: Dict[Tuple[int, int], Tuple[float, float]]) -> None:
        with self._lock:
            if self._grid is None:
                return

            changed = False
            for (y, x), (vx, vy) in updates.items():
                if 0 <= y < self._grid.shape[0] and 0 <= x < self._grid.shape[1]:
                    self._grid[y, x] = (vx, vy)
                    changed = True

            if changed:
                self._state_manager.set("grid_updated", True)

                self._event_bus.publish(Event(
                    EventType.GRID_UPDATED,
                    {"updates": updates},
                    "GridManager"
                ))

    def clear_grid(self) -> None:
        with self._lock:
            if self._grid is not None:
                self._grid.fill(0.0)

                self._state_manager.set("grid_updated", True, notify=False)

                self._event_bus.publish(Event(
                    EventType.GRID_CLEARED,
                    {},
                    "GridManager"
                ))

    def load_grid(self, file_path: str) -> bool:
        try:
            if not os.path.exists(file_path):
                print(f"[GridManager] File not found: {file_path}")
                return False

            loaded_grid = np.load(file_path)

            with self._lock:
                if self._grid is not None and loaded_grid.shape != self._grid.shape:
                    print(f"[GridManager] Grid size mismatch: {loaded_grid.shape} vs {self._grid.shape}")
                    return False

                self._grid = loaded_grid.copy()

                self._state_manager.update({
                    "grid_width": loaded_grid.shape[1],
                    "grid_height": loaded_grid.shape[0],
                    "grid_updated": True
                })

                self._event_bus.publish(Event(
                    EventType.GRID_LOADED,
                    {"file_path": file_path, "shape": loaded_grid.shape},
                    "GridManager"
                ))

                return True
        except Exception as e:
            print(f"[GridManager] Failed to load grid: {e}")
            return False

    def save_grid(self, file_path: str) -> bool:
        try:
            with self._lock:
                if self._grid is not None:
                    np.save(file_path, self._grid)

                    self._event_bus.publish(Event(
                        EventType.GRID_SAVED,
                        {"file_path": file_path, "shape": self._grid.shape},
                        "GridManager"
                    ))

                    return True
            return False
        except Exception as e:
            print(f"[GridManager] Failed to save grid: {e}")
            return False

    def handle(self, event: Event) -> None:
        if event.type == EventType.CLEAR_GRID:
            self.clear_grid()
        elif event.type == EventType.TOGGLE_GRID:
            show_grid = self._state_manager.get("show_grid", True)
            self._state_manager.set("show_grid", not show_grid)

class ViewManager(EventHandler):
    def __init__(self, state_manager: StateManager, event_bus: EventBus):
        self._state_manager = state_manager
        self._event_bus = event_bus

        # init view state
        self._state_manager.update({
            "cam_x": 0.0,
            "cam_y": 0.0,
            "cam_zoom": 1.0,
            "view_changed": False,
        })

        self._event_bus.subscribe(EventType.RESET_VIEW, self)

    def reset_view(self, width: int = 640, height: int = 480) -> None:
        cell_size = config_manager.get("cell_size", 1.0)
        cam_x = (width * cell_size) / 2.0
        cam_y = (height * cell_size) / 2.0
        cam_zoom = config_manager.get("cam_zoom", 1.0)

        self._state_manager.update({
            "cam_x": cam_x,
            "cam_y": cam_y,
            "cam_zoom": cam_zoom,
            "view_changed": True
        })

        self._event_bus.publish(Event(
            EventType.VIEW_RESET,
            {"cam_x": cam_x, "cam_y": cam_y, "cam_zoom": cam_zoom},
            "ViewManager"
        ))

    def handle(self, event: Event) -> None:
        if event.type == EventType.RESET_VIEW:
            width = self._state_manager.get("grid_width", 640)
            height = self._state_manager.get("grid_height", 480)
            self.reset_view(width, height)

class AppCore:
    def __init__(self):
        self._state_manager = state_manager
        self._event_bus = event_bus
        self._config_manager = config_manager

        # init managers
        self._grid_manager = GridManager(self._state_manager, self._event_bus)
        self._view_manager = ViewManager(self._state_manager, self._event_bus)
        self._fps_limiter = FPSLimiter(self._state_manager, self._event_bus, self._config_manager)

        # get services from container
        self._vector_calculator = container.resolve(VectorFieldCalculator)
        self._renderer = container.resolve(VectorFieldRenderer)

        # if not in container, create them
        if self._vector_calculator is None:
            self._vector_calculator = VectorFieldCalculator()
            container.register_singleton(VectorFieldCalculator, self._vector_calculator)

        if self._renderer is None:
            self._renderer = VectorFieldRenderer()
            container.register_singleton(VectorFieldRenderer, self._renderer)

        # register self to container
        container.register_singleton(AppCore, self)

        # publish app init event
        self._event_bus.publish(Event(
            EventType.APP_INITIALIZED,
            {},
            "AppCore"
        ))

    @property
    def state_manager(self) -> StateManager:
        return self._state_manager

    @property
    def event_bus(self) -> Event:
        return self._event_bus

    @property
    def config_manager(self) -> ConfigManager:
        return self._config_manager

    @property
    def grid_manager(self) -> GridManager:
        return self._grid_manager

    @property
    def view_manager(self) -> ViewManager:
        return self._view_manager

    @property
    def fps_limiter(self) -> FPSLimiter:
        return self._fps_limiter

    @property
    def vector_calculator(self) -> VectorFieldCalculator:
        return self._vector_calculator

    @property
    def renderer(self) -> VectorFieldRenderer:
        return self._renderer

    def shutdown(self) -> None:
        # publish shutdown event
        self._event_bus.publish(Event(
            EventType.APP_SHUTDOWN,
            {},
            "AppCore"
        ))

        # cleanup resources
        self._state_manager.clear_listeners()
        self._event_bus.clear()

        if self._renderer:
            self._renderer.cleanup()

# register services to container
container.register_singleton(StateManager, state_manager)
container.register_singleton(ConfigManager, config_manager)
container.register_singleton(Event, event_bus)
