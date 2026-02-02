
import glfw
import numpy as np
from typing import Dict, Any, Optional, Callable, List, Tuple
from ..core.events import Event, EventType, event_bus, EventHandler
from ..core.state import state_manager


class InputHandler(EventHandler):
    

    def __init__(self):
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._key_states = {}
        self._mouse_buttons = {}
        self._mouse_position = (0.0, 0.0)
        self._mouse_scroll = (0.0, 0.0)
        self._key_callbacks = {}
        self._mouse_callbacks = {}

    def register_key_callback(self, key: int, action: int, callback: Callable):
        
        key_id = f"{key}_{action}"
        self._key_callbacks[key_id] = callback

    def register_mouse_callback(self, button: int, action: int, callback: Callable):
        
        button_id = f"{button}_{action}"
        self._mouse_callbacks[button_id] = callback

    def is_key_pressed(self, key: int) -> bool:
        
        return self._key_states.get(key, False)

    def is_mouse_button_pressed(self, button: int) -> bool:
        
        return self._mouse_buttons.get(button, False)

    def get_mouse_position(self) -> Tuple[float, float]:
        
        return self._mouse_position

    def get_mouse_scroll(self) -> Tuple[float, float]:
        
        return self._mouse_scroll
        
    def reset_mouse_scroll(self) -> None:
        
        self._mouse_scroll = (0.0, 0.0)

    def handle_key_event(self, window, key: int, scancode: int, action: int, mods: int):
        
        # updatekeystate
        if action == glfw.PRESS:
            self._key_states[key] = True
        elif action == glfw.RELEASE:
            self._key_states[key] = False

        event_type = EventType.KEY_PRESSED if action == glfw.PRESS else EventType.KEY_RELEASED
        event = Event(
            type=event_type,
            data={
                "key": key,
                "scancode": scancode,
                "action": action,
                "mods": mods
            }
        )
        event_bus.publish(event)

        key_id = f"{key}_{action}"
        if key_id in self._key_callbacks:
            self._key_callbacks[key_id]()

    def handle_mouse_button_event(self, window, button: int, action: int, mods: int):
        
        if action == glfw.PRESS:
            self._mouse_buttons[button] = True
        elif action == glfw.RELEASE:
            self._mouse_buttons[button] = False

        x, y = glfw.get_cursor_pos(window)

        event = Event(
            type=EventType.MOUSE_CLICKED,
            data={
                "button": button,
                "action": action,
                "mods": mods,
                "position": (x, y)
            }
        )
        self._event_bus.publish(event)

        button_id = f"{button}_{action}"
        if button_id in self._mouse_callbacks:
            self._mouse_callbacks[button_id]()

    def handle_cursor_position_event(self, window, x: float, y: float):
        
        dx = x - self._mouse_position[0]
        dy = y - self._mouse_position[1]

        # updatemouseposition
        self._mouse_position = (x, y)

        event = Event(
            type=EventType.MOUSE_MOVED,
            data={
                "position": (x, y),
                "delta": (dx, dy)
            }
        )
        event_bus.publish(event)

    def handle_scroll_event(self, window, x: float, y: float):
        
        # updatescrollposition
        self._mouse_scroll = (x, y)

        event = Event(
            type=EventType.MOUSE_SCROLLED,
            data={
                "offset": (x, y)
            }
        )
        event_bus.publish(event)


input_handler = InputHandler()
