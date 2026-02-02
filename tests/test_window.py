import pytest
import numpy as np
import warnings
from unittest.mock import Mock, MagicMock, patch
from OpenGL.GL import GL_LINE_SMOOTH_HINT, GL_NICEST
from glfw import GLFWError
from gravitas.window.window import Window
from gravitas.core.events import EventType, event_bus
from gravitas.core.state import state_manager


class TestWindow:
    

    def setup_method(self):
        
        self.window = Window("Test Window", 800, 600)
        warnings.filterwarnings("ignore", message=".*GLFW.*")

    @patch('glfw.init')
    @patch('glfw.create_window')
    @patch('glfw.make_context_current')
    @patch('glfw.set_framebuffer_size_callback')
    @patch('glfw.set_key_callback')
    @patch('glfw.set_mouse_button_callback')
    @patch('glfw.set_cursor_pos_callback')
    @patch('glfw.set_scroll_callback')
    @patch('gravitas.window.window.glViewport')
    @patch('gravitas.window.window.glClearColor')
    @patch('gravitas.window.window.glEnable')
    @patch('gravitas.window.window.glHint')
    def test_initialize_success(self, mock_glHint, mock_glEnable, mock_glClearColor,
                               mock_glViewport, mock_scroll_callback, mock_cursor_pos_callback,
                               mock_mouse_button_callback, mock_key_callback,
                               mock_framebuffer_size_callback, mock_make_context_current,
                               mock_create_window, mock_init):
        
        mock_init.return_value = True
        mock_create_window.return_value = Mock()  # Mock window object

        with patch('gravitas.window.window.VectorFieldRenderer') as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            result = self.window.initialize()

            assert result == True
            assert self.window._window is not None
            assert self.window._renderer is not None
            mock_init.assert_called_once()
            mock_create_window.assert_called_once_with(800, 600, "Test Window", None, None)

    @patch('glfw.init')
    def test_initialize_glfw_failure(self, mock_init):
        
        mock_init.return_value = False

        result = self.window.initialize()

        assert result == False

    @patch('glfw.init')
    @patch('glfw.create_window')
    @patch('glfw.terminate')
    def test_initialize_window_creation_failure(self, mock_terminate, mock_create_window, mock_init):
        
        mock_init.return_value = True
        mock_create_window.return_value = None

        result = self.window.initialize()

        assert result == False
        mock_terminate.assert_called_once()

    @patch('glfw.destroy_window')
    @patch('glfw.terminate')
    def test_cleanup_on_failure(self, mock_terminate, mock_destroy_window):
        
        mock_window = Mock()
        self.window._window = mock_window
        self.window._cleanup_on_failure()

        mock_destroy_window.assert_called_once_with(mock_window)
        mock_terminate.assert_called_once()

    @patch('gravitas.window.window.glViewport')
    @patch('gravitas.window.window.glClearColor')
    @patch('gravitas.window.window.glEnable')
    @patch('gravitas.window.window.glHint')
    def test_init_opengl(self, mock_glHint, mock_glEnable, mock_glClearColor, mock_glViewport):
        
        self.window._init_opengl()

        mock_glViewport.assert_called_once_with(0, 0, 800, 600)
        mock_glClearColor.assert_called_once_with(0.1, 0.1, 0.1, 1.0)
        mock_glEnable.assert_called()
        mock_glHint.assert_called_once_with(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def test_register_event_handlers(self):
        
        self.window._register_event_handlers()

        assert EventType.MOUSE_CLICKED in self.window._event_handlers
        assert EventType.MOUSE_MOVED in self.window._event_handlers
        assert EventType.MOUSE_SCROLLED in self.window._event_handlers
        assert EventType.KEY_PRESSED in self.window._event_handlers
        assert EventType.KEY_RELEASED in self.window._event_handlers

    @patch('gravitas.window.window.glViewport')
    @patch('gravitas.window.window.event_bus')
    def test_framebuffer_size_callback(self, mock_event_bus, mock_glViewport):
        
        mock_window = Mock()

        self.window._framebuffer_size_callback(mock_window, 1024, 768)

        assert self.window._width == 1024
        assert self.window._height == 768
        assert self.window._state_manager.get("viewport_width") == 1024
        assert self.window._state_manager.get("viewport_height") == 768
        mock_event_bus.publish.assert_called_once()
        mock_glViewport.assert_called_once_with(0, 0, 1024, 768)

    @patch('gravitas.window.window.input_handler.handle_key_event')
    def test_key_callback(self, mock_handle_key_event):
        
        mock_window = Mock()

        # Test key press
        self.window._key_callback(mock_window, 65, 0, 1, 0)  # A key press
        assert self.window._keys[65] == True
        mock_handle_key_event.assert_called_once_with(mock_window, 65, 0, 1, 0)

        # Test key release
        mock_handle_key_event.reset_mock()
        self.window._key_callback(mock_window, 65, 0, 0, 0)  # A key release
        assert self.window._keys[65] == False
        mock_handle_key_event.assert_called_once_with(mock_window, 65, 0, 0, 0)

    @patch('gravitas.window.window.input_handler.handle_mouse_button_event')
    @patch('glfw.get_cursor_pos')
    def test_mouse_button_callback(self, mock_get_cursor_pos, mock_handle_mouse_button):
        
        mock_window = Mock()
        mock_get_cursor_pos.return_value = (100.0, 200.0)

        # Test mouse press
        self.window._mouse_button_callback(mock_window, 0, 1, 0)  # Left button press
        assert self.window._mouse_pressed == True
        assert self.window._last_mouse_x == 100.0
        assert self.window._last_mouse_y == 200.0
        mock_handle_mouse_button.assert_called_once_with(mock_window, 0, 1, 0)

        # Test mouse release
        mock_handle_mouse_button.reset_mock()
        self.window._mouse_button_callback(mock_window, 0, 0, 0)  # Left button release
        assert self.window._mouse_pressed == False
        mock_handle_mouse_button.assert_called_once_with(mock_window, 0, 0, 0)

    @patch('gravitas.window.window.input_handler.handle_cursor_position_event')
    def test_cursor_pos_callback(self, mock_handle_cursor_pos):
        
        mock_window = Mock()

        self.window._cursor_pos_callback(mock_window, 150.0, 250.0)

        assert self.window._mouse_x == 150.0
        assert self.window._mouse_y == 250.0
        mock_handle_cursor_pos.assert_called_once_with(mock_window, 150.0, 250.0)

    @patch('gravitas.window.window.input_handler.handle_scroll_event')
    def test_scroll_callback(self, mock_handle_scroll):
        
        mock_window = Mock()

        self.window._scroll_callback(mock_window, 1.0, -1.0)

        assert self.window._scroll_y == -1.0
        mock_handle_scroll.assert_called_once_with(mock_window, 1.0, -1.0)

    def test_handle_mouse_click(self):
        
        event = Mock()
        event.data = {"button": 0, "action": 1}

        # Should not raise exception
        self.window._handle_mouse_click(event)

    @patch('gravitas.core.events.event_bus')
    def test_handle_mouse_move(self, mock_event_bus):
        
        # Set up initial state
        self.window._mouse_pressed = True
        self.window._mouse_x = 150.0
        self.window._mouse_y = 250.0
        self.window._last_mouse_x = 100.0
        self.window._last_mouse_y = 200.0

        event = Mock()
        event.data = {"position": (150.0, 250.0), "delta": (50.0, 50.0)}

        self.window._handle_mouse_move(event)

        # Camera position should be updated
        assert self.window._state_manager.get("cam_x") == -5.0  # -50 * 0.1
        assert self.window._state_manager.get("cam_y") == 5.0   # +50 * 0.1
        assert self.window._state_manager.get("view_changed") == True

    def test_handle_mouse_scroll(self):
        
        event = Mock()
        event.data = {"xoffset": 0.0, "yoffset": 1.0}

        self.window._handle_mouse_scroll(event)

        # Camera zoom should be decreased
        expected_zoom = 1.0 - 1.0 * 0.1  # 0.9
        assert self.window._state_manager.get("cam_zoom") == expected_zoom
        assert self.window._state_manager.get("view_changed") == True

    @patch('gravitas.core.events.event_bus')
    def test_handle_key_press_escape(self, mock_event_bus):
        
        event = Mock()
        event.data = {"key": 256}  # GLFW_KEY_ESCAPE

        self.window._handle_key_press(event)

        assert self.window.should_close == True

    @patch('gravitas.window.window.event_bus')
    def test_handle_key_press_r(self, mock_event_bus):
        
        self.window._event_bus = mock_event_bus
        event = Mock()
        event.data = {"key": 82}  # GLFW_KEY_R

        self.window._handle_key_press(event)

        mock_event_bus.publish.assert_called_once()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert published_event.type == EventType.RESET_VIEW

    def test_handle_key_press_g(self):
        
        mock_event_bus = Mock()
        self.window._event_bus = mock_event_bus

        event = Mock()
        event.data = {"key": 71}  # GLFW_KEY_G

        self.window._handle_key_press(event)

        mock_event_bus.publish.assert_called_once()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert published_event.type == EventType.TOGGLE_GRID

    @patch('gravitas.window.window.event_bus')
    def test_handle_key_press_c(self, mock_event_bus):
        
        self.window._event_bus = mock_event_bus
        event = Mock()
        event.data = {"key": 67}  # GLFW_KEY_C

        self.window._handle_key_press(event)

        mock_event_bus.publish.assert_called_once()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert published_event.type == EventType.CLEAR_GRID

    def test_handle_key_release(self):
        
        event = Mock()

        # Should not raise exception
        self.window._handle_key_release(event)

    def test_handle_app_initialized(self):
        
        event = Mock()
        event.type = EventType.APP_INITIALIZED
        event.data = {"width": 1024, "height": 768}

        self.window.handle(event)

        assert self.window._width == 1024
        assert self.window._height == 768

    @patch('glfw.window_should_close')
    def test_should_close_property(self, mock_window_should_close):
        
        mock_window_should_close.return_value = False

        # Initially should not close
        assert not self.window.should_close

        # Set should close
        self.window.should_close = True
        assert self.window.should_close

        # Test GLFW close
        self.window._should_close = False
        mock_window_should_close.return_value = True
        assert self.window.should_close

    def test_close(self):
        
        self.window.close()
        assert self.window.should_close == True

    @patch('glfw.poll_events')
    def test_update(self, mock_poll_events):
        
        self.window.update()
        mock_poll_events.assert_called_once()

    @patch('glfw.swap_buffers')
    def test_render(self, mock_swap_buffers):
        
        # Set up mock renderer
        mock_renderer = Mock()
        self.window._renderer = mock_renderer

        # Set up mock window
        mock_window = Mock()
        self.window._window = mock_window

        # Create test grid
        grid = np.zeros((10, 10, 2), dtype=np.float32)

        self.window.render(grid)

        # Check that renderer methods were called
        mock_renderer.render_background.assert_called_once()
        mock_renderer.render_markers.assert_called_once()
        mock_renderer.render_vector_field.assert_called_once()
        mock_renderer.render_grid.assert_called_once()
        mock_swap_buffers.assert_called_once_with(mock_window)

    @patch('glfw.destroy_window')
    @patch('glfw.terminate')
    def test_cleanup(self, mock_terminate, mock_destroy_window):
        
        mock_window = Mock()
        self.window._window = mock_window

        self.window.cleanup()

        mock_destroy_window.assert_called_once_with(mock_window)
        mock_terminate.assert_called_once()
        assert self.window._window is None


if __name__ == "__main__":
    pytest.main([__file__])
