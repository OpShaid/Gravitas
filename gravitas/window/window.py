
import glfw
import numpy as np
from OpenGL.GL import *
from typing import Optional, Callable, Dict, Any, Tuple
from ..core.events import Event, EventType, event_bus, EventHandler, FunctionEventHandler
from ..core.state import state_manager
from ..graphics.renderer import VectorFieldRenderer
from ..input import input_handler

class Window(EventHandler):
    
    def __init__(self, title: str = "LiziEngine", width: int = 800, height: int = 600):
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._renderer = None

        self._title = title
        self._width = width
        self._height = height
        self._window = None
        self._should_close = False

        # mousestate
        self._mouse_pressed = False
        self._mouse_x = 0
        self._mouse_y = 0
        self._last_mouse_x = 0
        self._last_mouse_y = 0
        self._scroll_y = 0

        # keyboardstate
        self._keys = {}

        # eventhandler
        self._event_handlers = {}

        # subscribeevent
        self._event_bus.subscribe(EventType.APP_INITIALIZED, self)

    def initialize(self) -> bool:
        
        try:
            # initializeGLFW
            if not glfw.init():
                print("[window] GLFWinitializefail")
                return False

            # configGLFW
            glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

            # createwindow
            self._window = glfw.create_window(self._width, self._height, self._title, None, None)

            if not self._window:
                print("[window] windowcreatefail")
                glfw.terminate()
                return False

            glfw.make_context_current(self._window)

            # setwindowcallback
            glfw.set_framebuffer_size_callback(self._window, self._framebuffer_size_callback)
            glfw.set_key_callback(self._window, self._key_callback)
            glfw.set_mouse_button_callback(self._window, self._mouse_button_callback)
            glfw.set_cursor_pos_callback(self._window, self._cursor_pos_callback)
            glfw.set_scroll_callback(self._window, self._scroll_callback)

            # initializeOpenGL
            self._init_opengl()

            try:
                from ..core.container import container
                self._renderer = container.resolve(VectorFieldRenderer)

                if self._renderer is None:
                    self._renderer = VectorFieldRenderer()
                    container.register_singleton(VectorFieldRenderer, self._renderer)
            except Exception as e:
                print(f"[window] getrenderfail，createinstance: {e}")
                self._renderer = VectorFieldRenderer()

            # registereventhandler
            self._register_event_handlers()

            print("[window] initializesuccess")
            return True
        except Exception as e:
            print(f"[window] initializefail: {e}")
            self._cleanup_on_failure()
            return False

    def _cleanup_on_failure(self) -> None:
        
        try:
            if self._window:
                glfw.destroy_window(self._window)
                self._window = None
            glfw.terminate()
        except Exception as e:
            print(f"[window] failresourcehour: {e}")

    def _init_opengl(self) -> None:
        
        glEnable(GL_DEPTH_TEST)

        glViewport(0, 0, self._width, self._height)

        # setclearcolor
        glClearColor(0.1, 0.1, 0.1, 1.0)

        if self._state_manager.get("antialiasing", True):
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def _register_event_handlers(self) -> None:
        
        # mouseclickevent
        self._event_handlers[EventType.MOUSE_CLICKED] = FunctionEventHandler(
            self._handle_mouse_click, "WindowMouseClickHandler"
        )

        self._event_handlers[EventType.MOUSE_MOVED] = FunctionEventHandler(
            self._handle_mouse_move, "WindowMouseMoveHandler"
        )

        # mousescrollevent
        self._event_handlers[EventType.MOUSE_SCROLLED] = FunctionEventHandler(
            self._handle_mouse_scroll, "WindowMouseScrollHandler"
        )

        # keyboardpressedevent
        self._event_handlers[EventType.KEY_PRESSED] = FunctionEventHandler(
            self._handle_key_press, "WindowKeyPressHandler"
        )

        self._event_handlers[EventType.KEY_RELEASED] = FunctionEventHandler(
            self._handle_key_release, "WindowKeyReleaseHandler"
        )

    def _framebuffer_size_callback(self, window, width, height):
        
        self._width = width
        self._height = height

        glViewport(0, 0, width, height)

        # updatestate
        self._state_manager.set("viewport_width", width)
        self._state_manager.set("viewport_height", height)

        event_bus.publish(Event(
            EventType.VIEW_CHANGED,
            {"width": width, "height": height},
            "Window"
        ))

    def _key_callback(self, window, key, scancode, action, mods):
        
        # updatekeyboardstate
        if action == glfw.PRESS:
            self._keys[key] = True
        elif action == glfw.RELEASE:
            self._keys[key] = False
            
        input_handler.handle_key_event(window, key, scancode, action, mods)

    def _mouse_button_callback(self, window, button, action, mods):
        
        if action == glfw.PRESS:
            self._mouse_pressed = True
            self._last_mouse_x, self._last_mouse_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            self._mouse_pressed = False
            
        input_handler.handle_mouse_button_event(window, button, action, mods)

    def _cursor_pos_callback(self, window, xpos, ypos):
        
        self._mouse_x = xpos
        self._mouse_y = ypos
        
        input_handler.handle_cursor_position_event(window, xpos, ypos)

    def _scroll_callback(self, window, xoffset, yoffset):
        
        self._scroll_y = yoffset
        input_handler.handle_scroll_event(window, xoffset, yoffset)

    def _handle_mouse_click(self, event: Event) -> None:
        
        pass

    def _handle_mouse_move(self, event: Event) -> None:
        
        if self._mouse_pressed:
            dx = self._mouse_x - self._last_mouse_x
            dy = self._mouse_y - self._last_mouse_y

            cam_speed = 0.1
            cam_x = self._state_manager.get("cam_x", 0.0) - dx * cam_speed
            cam_y = self._state_manager.get("cam_y", 0.0) + dy * cam_speed

            self._state_manager.update({
                "cam_x": cam_x,
                "cam_y": cam_y,
                "view_changed": True
            })

            self._last_mouse_x = self._mouse_x
            self._last_mouse_y = self._mouse_y

    def _handle_mouse_scroll(self, event: Event) -> None:
        
        xoffset = event.data.get("xoffset", 0)
        yoffset = event.data.get("yoffset", 0)

        cam_zoom = self._state_manager.get("cam_zoom", 1.0)
        zoom_speed = 0.1
        cam_zoom -= yoffset * zoom_speed

        cam_zoom = max(0.1, min(10.0, cam_zoom))

        self._state_manager.update({
            "cam_zoom": cam_zoom,
            "view_changed": True
        })

    def _handle_key_press(self, event: Event) -> None:
        
        key = event.data.get("key")

        if key == glfw.KEY_ESCAPE:
            self.should_close = True
        elif key == glfw.KEY_R:
            self._event_bus.publish(Event(
                EventType.RESET_VIEW,
                {},
                "Window"
            ))
        elif key == glfw.KEY_G:
            # toggle grid show
            self._event_bus.publish(Event(
                EventType.TOGGLE_GRID,
                {},
                "Window"
            ))
        elif key == glfw.KEY_C:
            # clear grid
            self._event_bus.publish(Event(
                EventType.CLEAR_GRID,
                {},
                "Window"
            ))

    def _handle_key_release(self, event: Event) -> None:
        
        pass

    def handle(self, event: Event) -> None:
        
        if event.type == EventType.APP_INITIALIZED:
            if "width" in event.data and "height" in event.data:
                self._width = event.data["width"]
                self._height = event.data["height"]

    @property
    def should_close(self) -> bool:
        
        return self._should_close or glfw.window_should_close(self._window)

    @should_close.setter
    def should_close(self, value: bool) -> None:
        
        self._should_close = value

    def close(self) -> None:
        
        self.should_close = True

    def update(self) -> None:
        
        # updateGLFWevent
        glfw.poll_events()

    def render(self, grid: np.ndarray) -> None:
        
        if not self._window or not self._renderer:
            return

        self._renderer.render_background()

        cam_x = self._state_manager.get("cam_x", 0.0)
        cam_y = self._state_manager.get("cam_y", 0.0)
        cam_zoom = self._state_manager.get("cam_zoom", 1.0)

        viewport_width = self._state_manager.get("viewport_width", self._width)
        viewport_height = self._state_manager.get("viewport_height", self._height)

        try:
            self._renderer.render_markers(
                cell_size=self._state_manager.get("cell_size", 1.0),
                cam_x=cam_x,
                cam_y=cam_y,
                cam_zoom=cam_zoom,
                viewport_width=viewport_width,
                viewport_height=viewport_height
            )
        except Exception:
            pass

        # rendervector field
        self._renderer.render_vector_field(
            grid,
            cell_size=self._state_manager.get("cell_size", 1.0),
            cam_x=cam_x,
            cam_y=cam_y,
            cam_zoom=cam_zoom,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        )

        # rendergrid
        self._renderer.render_grid(
            grid,
            cell_size=self._state_manager.get("cell_size", 1.0),
            cam_x=cam_x,
            cam_y=cam_y,
            cam_zoom=cam_zoom,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        )



        glfw.swap_buffers(self._window)

    def cleanup(self) -> None:
        
        if self._window:
            glfw.destroy_window(self._window)
            self._window = None

        glfw.terminate()
        print("[window] resourcedone")
