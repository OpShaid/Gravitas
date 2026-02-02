
from typing import Tuple
import numpy as np
from gravitas.input import input_handler, KeyMap, MouseMap


class UIManager:
    def __init__(self, app_core, window, controller, marker_system, command_input_handler=None):
        self.app_core = app_core
        self.window = window
        self.controller = controller
        self.marker_system = marker_system
        self.command_input_handler = command_input_handler

        self.enable_update = True

        self._last_mouse_x = None
        self._last_mouse_y = None

        self._mouse_left_pressed = False

        self._selected_marker = None

        self._mouse_middle_pressed = False

    def register_callbacks(self, grid: np.ndarray, on_space=None, on_r=None, on_g=None, on_c=None, on_u=None, on_v=None, on_f=None):
        self._grid = grid

        def on_space_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_space):
                try:
                    on_space()
                    return
                except Exception as e:
                    print(f"[error] on_space callbackexception: {e}")

        def on_r_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_r):
                try:
                    on_r()
                    return
                except Exception as e:
                    print(f"[error] on_r callbackexception: {e}")
            try:
                self.controller.reset_view()
            except Exception as e:
                print(f"[error] reset_view exception: {e}")

        def on_g_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_g):
                try:
                    on_g()
                    return
                except Exception as e:
                    print(f"[error] on_g callbackexception: {e}")
            try:
                self.controller.toggle_grid()
            except Exception as e:
                print(f"[error] toggle_grid exception: {e}")

        def on_c_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_c):
                try:
                    on_c()
                    return
                except Exception as e:
                    print(f"[error] on_c callbackexception: {e}")
            try:
                self.controller.clear_grid()
            except Exception as e:
                print(f"[error] clear_grid exception: {e}")
            try:
                self.marker_system.clear_markers()
            except Exception as e:
                print(f"[error] clear_markers exception: {e}")

        def on_v_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_v):
                try:
                    on_v()
                    return
                except Exception as e:
                    print(f"[error] on_v callbackexception: {e}")
            try:
                self.controller.switch_vector_field_direction()
            except Exception as e:
                print(f"[error] switch_vector_field_direction exception: {e}")

        def on_u_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_u):
                try:
                    on_u()
                    return
                except Exception as e:
                    print(f"[error] on_u callbackexception: {e}")

        def on_f_press():
            if self.command_input_handler and self.command_input_handler.command_mode:
                return
            if callable(on_f):
                try:
                    on_f()
                    return
                except Exception as e:
                    print(f"[error] on_f callbackexception: {e}")
            try:
                mx, my = input_handler.get_mouse_position()
                self.controller.place_vector_field(mx, my)
            except Exception as e:
                print(f"[error] handlerfkeypressedhourexception: {e}")

        def on_mouse_left_press():
            try:
                self._mouse_left_pressed = True

                mx, my = input_handler.get_mouse_position()
                self._selected_marker = self.controller.handle_mouse_left_press(mx, my)
            except Exception as e:
                print(f"[error] handlermouseleftkeypressedhourexception: {e}")

        input_handler.register_key_callback(KeyMap.SPACE, MouseMap.PRESS, on_space_press)
        input_handler.register_key_callback(KeyMap.R, MouseMap.PRESS, on_r_press)
        input_handler.register_key_callback(KeyMap.G, MouseMap.PRESS, on_g_press)
        input_handler.register_key_callback(KeyMap.C, MouseMap.PRESS, on_c_press)
        input_handler.register_key_callback(KeyMap.U, MouseMap.PRESS, on_u_press)
        input_handler.register_key_callback(KeyMap.V, MouseMap.PRESS, on_v_press)
        input_handler.register_key_callback(KeyMap.F, MouseMap.PRESS, on_f_press)

        input_handler.register_mouse_callback(MouseMap.LEFT, MouseMap.PRESS, on_mouse_left_press)

        def on_mouse_left_release():
            self._mouse_left_pressed = False
            self._selected_marker = None

        input_handler.register_mouse_callback(MouseMap.LEFT, MouseMap.RELEASE, on_mouse_left_release)

        def on_mouse_middle_press():
            self._mouse_middle_pressed = True

        def on_mouse_middle_release():
            self._mouse_middle_pressed = False

        input_handler.register_mouse_callback(MouseMap.MIDDLE, MouseMap.PRESS, on_mouse_middle_press)
        input_handler.register_mouse_callback(MouseMap.MIDDLE, MouseMap.RELEASE, on_mouse_middle_release)

    def process_mouse_drag(self):
        window = self.window
        if self._mouse_left_pressed and self._selected_marker is not None:
            try:
                mx, my = window._mouse_x, window._mouse_y
                self.controller.handle_mouse_drag(mx, my, self._selected_marker)
            except Exception as e:
                print(f"[error] handlerleftkeyheld downhourexception: {e}")

        if self._mouse_middle_pressed:
            x, y = window._mouse_x, window._mouse_y

            dx = x - (self._last_mouse_x if self._last_mouse_x is not None else x)
            dy = y - (self._last_mouse_y if self._last_mouse_y is not None else y)

            try:
                self.controller.handle_mouse_drag_view(dx, dy)
            except Exception as e:
                print(f"[error] process_mouse_drag_view exception: {e}")

            self._last_mouse_x = x
            self._last_mouse_y = y
        else:
            # clearlastposition，avoidnextdragjump
            self._last_mouse_x = None
            self._last_mouse_y = None

    def process_scroll(self):
        window = self.window
        if hasattr(window, "_scroll_y") and window._scroll_y != 0:
            try:
                self.controller.handle_scroll_zoom(window._scroll_y)
            except Exception as e:
                print(f"[error] process_scroll exception: {e}")

            window._scroll_y = 0
