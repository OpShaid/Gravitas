
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gravitas.core.app import AppCore
from gravitas.window.window import Window
from gravitas.input import input_handler, KeyMap, MouseMap


class InputDemoApp:
    

    def __init__(self):
        self._app_core = AppCore()
        self._window = Window()
        self._init_input_handlers()

    def _init_input_handlers(self):
        
        # registerkeyboardcallback
        input_handler.register_key_callback(KeyMap.ESCAPE, MouseMap.PRESS, self._on_escape_press)
        input_handler.register_key_callback(KeyMap.SPACE, MouseMap.PRESS, self._on_space_press)

        # registermousecallback
        input_handler.register_mouse_callback(MouseMap.LEFT, MouseMap.PRESS, self._on_left_click)

    def _on_escape_press(self):
        
        print("ESCkeypressed，quitapply")
        self.shutdown()
        
    def shutdown(self):
        
        self._app_core.shutdown()
        
    def run(self):
        
        # initializewindow
        if not self._window.initialize():
            print("[error] window init failed")
            return
            
        import numpy as np
        grid = np.zeros((10, 10, 2), dtype=np.float32)
            
        while not self._window.should_close:
            # updateinputstate
            self.update(0.016)
            
            # render
            self._window.render(grid)
            
            self._window.update()
            
        self._window.cleanup()
        self.shutdown()

    def _on_space_press(self):
        
        print("emptykeypressed")

    def _on_left_click(self):
        
        x, y = input_handler.get_mouse_position()
        print(f"mouseleftkeyclickposition: ({x:.2f}, {y:.2f})")

    def update(self, dt):
        
        # checkkeystate
        if input_handler.is_key_pressed(KeyMap.UP):
            print("updirectionkeypressed")

        if input_handler.is_key_pressed(KeyMap.DOWN):
            print("downdirectionkeypressed")

        if input_handler.is_key_pressed(KeyMap.LEFT):
            print("leftdirectionkeypressed")

        if input_handler.is_key_pressed(KeyMap.RIGHT):
            print("rightdirectionkeypressed")

        if input_handler.is_mouse_button_pressed(MouseMap.RIGHT):
            print("mouserightkeypressed")

        # getmouseposition
        x, y = input_handler.get_mouse_position()
        # print(f"mouseposition: ({x:.2f}, {y:.2f})")

        # getmousescrollposition
        scroll_x, scroll_y = input_handler.get_mouse_scroll()
        if scroll_y != 0:
            print(f"mousescroll: {scroll_y:.2f}")


if __name__ == "__main__":
    app = InputDemoApp()
    app.run()
