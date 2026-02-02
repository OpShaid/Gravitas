import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from gravitas.core.app import AppCore, GridManager, ViewManager, FPSLimiter
from gravitas.core.state import state_manager
from gravitas.core.events import event_bus, EventType
from gravitas.core.config import config_manager
from gravitas.core.container import container
from gravitas.compute.vector_field import VectorFieldCalculator
from gravitas.graphics.renderer import VectorFieldRenderer


class TestFPSLimiter:
    

    def setup_method(self):
        
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.fps_limiter = FPSLimiter(self.state_manager, self.event_bus, self.config_manager)

    def test_fps_limiter_initialization(self):
        
        assert self.fps_limiter.is_enabled()
        assert self.fps_limiter._enabled == True

    def test_fps_limiter_set_enabled(self):
        
        self.fps_limiter.set_enabled(False)
        assert not self.fps_limiter.is_enabled()

        self.fps_limiter.set_enabled(True)
        assert self.fps_limiter.is_enabled()

    def test_fps_limiter_limit_fps(self):
        
        original_fps = self.config_manager.get("target_fps")

        try:
            self.config_manager.set("target_fps", 10)

            import time
            start_time = time.time()
            self.fps_limiter.limit_fps()
            end_time = time.time()

            assert end_time - start_time >= 0.09
        finally:
            self.config_manager.set("target_fps", original_fps)

    @patch('gravitas.core.app.time.time')
    def test_fps_limiter_handle_config_change(self, mock_time):
        
        mock_time.return_value = 200.0

        event = Mock()
        event.type = EventType.CONFIG_CHANGED
        event.data = {"key": "target_fps"}

        old_time = self.fps_limiter._last_time
        self.fps_limiter.handle(event)

        assert self.fps_limiter._last_time == 200.0

    @patch('time.time')
    def test_fps_limiter_handle_other_config_change(self, mock_time):
        
        mock_time.return_value = 100.0

        event = Mock()
        event.type = EventType.CONFIG_CHANGED
        event.data = {"key": "other_setting"}

        old_time = self.fps_limiter._last_time
        self.fps_limiter.handle(event)

        assert self.fps_limiter._last_time == old_time


class TestGridManager:
    

    def setup_method(self):
        
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.grid_manager = GridManager(self.state_manager, self.event_bus)

    def test_grid_manager_initialization(self):
        
        assert self.grid_manager.grid is None
        assert self.state_manager.get("grid_width") == 640
        assert self.state_manager.get("grid_height") == 480

    def test_init_grid(self):
        
        grid = self.grid_manager.init_grid(100, 200)

        assert grid.shape == (200, 100, 2)
        assert np.all(grid == (0.0, 0.0))
        assert self.state_manager.get("grid_width") == 100
        assert self.state_manager.get("grid_height") == 200

    def test_init_grid_with_default(self):
        
        grid = self.grid_manager.init_grid(50, 50, (1.0, 2.0))

        assert grid.shape == (50, 50, 2)
        assert np.all(grid == (1.0, 2.0))

    def test_update_grid(self):
        
        self.grid_manager.init_grid(10, 10)
        updates = {(1, 1): (1.0, 2.0), (2, 2): (3.0, 4.0)}

        self.grid_manager.update_grid(updates)

        grid = self.grid_manager.grid
        assert grid[1, 1, 0] == 1.0
        assert grid[1, 1, 1] == 2.0
        assert grid[2, 2, 0] == 3.0
        assert grid[2, 2, 1] == 4.0

    def test_clear_grid(self):
        
        self.grid_manager.init_grid(10, 10)
        self.grid_manager.update_grid({(1, 1): (1.0, 1.0)})

        self.grid_manager.clear_grid()

        grid = self.grid_manager.grid
        assert np.all(grid == 0.0)

    def test_handle_clear_grid_event(self):
        
        self.grid_manager.init_grid(10, 10)
        self.grid_manager.update_grid({(1, 1): (1.0, 1.0)})

        event = Mock()
        event.type = EventType.CLEAR_GRID
        self.grid_manager.handle(event)

        grid = self.grid_manager.grid
        assert np.all(grid == 0.0)

    def test_handle_toggle_grid_event(self):
        
        event = Mock()
        event.type = EventType.TOGGLE_GRID
        self.grid_manager.handle(event)

        assert self.state_manager.get("show_grid") == False


class TestViewManager:
    

    def setup_method(self):
        
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.view_manager = ViewManager(self.state_manager, self.event_bus)

    def test_view_manager_initialization(self):
        
        assert self.state_manager.get("cam_x") == 0.0
        assert self.state_manager.get("cam_y") == 0.0
        assert self.state_manager.get("cam_zoom") == 1.0

    def test_reset_view(self):
        
        self.view_manager.reset_view(100, 200)

        expected_x = (100 * 1.0) / 2.0
        expected_y = (200 * 1.0) / 2.0

        assert self.state_manager.get("cam_x") == expected_x
        assert self.state_manager.get("cam_y") == expected_y
        assert self.state_manager.get("cam_zoom") == 1.0

    def test_handle_reset_view_event(self):
        
        event = Mock()
        event.type = EventType.RESET_VIEW

        self.view_manager.handle(event)

        assert self.state_manager.get("cam_x") != 0.0


class TestAppCore:
    

    def setup_method(self):
        
        container.clear()
        self.app_core = AppCore()

    def teardown_method(self):
        
        self.app_core.shutdown()
        container.clear()

    def test_app_core_initialization(self):
        
        assert self.app_core.state_manager is not None
        assert self.app_core.event_bus is not None
        assert self.app_core.config_manager is not None
        assert self.app_core.grid_manager is not None
        assert self.app_core.view_manager is not None
        assert self.app_core.fps_limiter is not None

    def test_app_core_services_registration(self):
        
        app_core_instance = container.resolve(AppCore)
        assert app_core_instance is not None
        assert isinstance(app_core_instance, AppCore)
        assert container.resolve(AppCore) is not None

    def test_app_core_vector_calculator(self):
        
        calculator = self.app_core.vector_calculator
        assert calculator is not None
        assert isinstance(calculator, VectorFieldCalculator)

    def test_app_core_renderer(self):
        
        renderer = self.app_core.renderer
        assert renderer is not None
        assert isinstance(renderer, VectorFieldRenderer)

    def test_app_core_shutdown(self):
        
        self.app_core.shutdown()

        assert self.app_core.renderer is not None


if __name__ == "__main__":
    pytest.main([__file__])
