
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravitas.core.container import container
from gravitas.core.app import AppCore
from gravitas.window.window import Window
from gravitas.compute.vector_field import vector_calculator
from gravitas.core.plugin import UIManager, Controller, MarkerSystem, add_inward_edge_vectors
from gravitas.input import input_handler, KeyMap, MouseMap
from plugins.command import Command, CommandInputHandler


class CommandDemoApp:
    

    def __init__(self):
        self.app_core = None
        self.window = None
        self.grid = None
        self.controller = None
        self.marker_system = None
        self.ui_manager = None
        self.command_plugin = None
        self.command_input_handler = None

        self._init_app()

    def _init_app(self):
        
        print("[instruction] startinginstructionplugindemo...")

        self.app_core = container.resolve(AppCore)
        if self.app_core is None:
            self.app_core = AppCore()
            container.register_singleton(AppCore, self.app_core)
        else:
            if isinstance(self.app_core, type):
                self.app_core = AppCore()
                container.register_singleton(AppCore, self.app_core)

        # initializewindow
        self.window = container.resolve(Window)
        if self.window is None:
            self.window = Window("LiziEngine instruction", 800, 600)
            container.register_singleton(Window, self.window)

        if not self.window.initialize():
            print("[instruction] window init failed")
            return

        # getgrid
        self.grid = self.app_core.grid_manager.init_grid(64, 64)

        try:
            self.app_core.view_manager.reset_view(self.grid.shape[1], self.grid.shape[0])
        except Exception:
            pass

        self.marker_system = MarkerSystem(self.app_core)

        # initializecontroller
        self.controller = Controller(self.app_core, vector_calculator, self.marker_system, self.grid)

        # initializeinstructionplugin
        self.command_plugin = Command(self.controller)

        # initializeinstructioninputhandler
        self.command_input_handler = CommandInputHandler(self.command_plugin)

        # initialize UI manager
        self.ui_manager = UIManager(self.app_core, self.window, self.controller, self.marker_system, self.command_input_handler)

        self.ui_manager.register_callbacks(self.grid)

        input_handler.register_key_callback(KeyMap.SLASH, MouseMap.PRESS, self.command_input_handler.get_toggle_callback())

        print("[instruction] press '/'keyactivateinstructioninput，press ESCquitinstruction，press Enterexecuteinstruction")



    def run(self):
        
        while not self.window.should_close:
            self.window.update()

            # clear grid
            self.grid.fill(0.0)

            try:
                self.ui_manager.process_mouse_drag()
            except Exception as e:
                print(f"[error] mouse drag error: {e}")

            self.ui_manager.process_scroll()

            if self.ui_manager.enable_update:
                add_inward_edge_vectors(self.grid, magnitude=1.0)
                try:
                    gravity = self.app_core.state_manager.get("gravity", 0.0)
                    speed_factor = self.app_core.state_manager.get("speed_factor", 0.99)
                    self.marker_system.update_field_and_markers(self.grid, dt=1.0, gravity=gravity, speed_factor=speed_factor)
                except Exception as e:
                    print(f"[error] update marker error: {e}")

            if self.command_input_handler.command_mode:
                self.command_input_handler._handle_command_input()

            # render
            self.window.render(self.grid)

            # FPS clamp
            self.app_core.fps_limiter.limit_fps()

        print("[instruction] cleaning resources...")
        self.window.cleanup()
        self.app_core.shutdown()

        print("[instruction] demo finished")


if __name__ == "__main__":
    app = CommandDemoApp()
    app.run()
