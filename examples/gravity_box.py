
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravitas.core.container import container
from gravitas.core.app import AppCore
from gravitas.window.window import Window
from gravitas.compute.vector_field import vector_calculator
from gravitas.core.plugin import UIManager, Controller, MarkerSystem, add_inward_edge_vectors

def main():
    
    print("[demo] startingLiziEnginebasic usagedemo...")

    app_core = container.resolve(AppCore)
    if app_core is None:
        app_core = AppCore()
        container.register_singleton(AppCore, app_core)
    else:
        if isinstance(app_core, type):
            app_core = AppCore()
            container.register_singleton(AppCore, app_core)

    # initializewindow
    window = container.resolve(Window)
    if window is None:
        window = Window("LiziEngine demo", 800, 600)
        container.register_singleton(Window, window)

    if not window.initialize():
        print("[demo] window init failed")
        return

    # getgrid
    grid = app_core.grid_manager.init_grid(64, 64)

    try:
        app_core.view_manager.reset_view(grid.shape[1], grid.shape[0])
    except Exception:
        pass

    print("[demo] starting main loop...")
    print("[demo] press space to regenerate tangent mode，press Gkeytoggle grid show，press Ckeyclear grid")
    print("[demo] press Ukeytoggle realtimeupdate；drag view with mouse and scroll to zoom")

    marker_system = MarkerSystem(app_core)

    # initializecontroller
    controller = Controller(app_core, vector_calculator, marker_system, grid)

    ui_manager = UIManager(app_core, window, controller, marker_system)


    def on_u_press():
        
        ui_manager.enable_update = not ui_manager.enable_update
        status = "enable" if ui_manager.enable_update else "disable"
        print(f"[demo] hourupdate: {status}")

    # registercallback
    ui_manager.register_callbacks(grid, on_u=on_u_press)

    while not window.should_close:
        window.update()

        #clear grid
        grid.fill(0.0)

        try:
            ui_manager.process_mouse_drag()
        except Exception as e:
            print(f"[error] mouse drag error: {e}")

        ui_manager.process_scroll()

        if ui_manager.enable_update:
            add_inward_edge_vectors(grid, magnitude=1.0)

            try:
                marker_system.update_field_and_markers(grid, dt=1.0, gravity=0.01, speed_factor=0.95)
            except Exception as e:
                print(f"[error] update marker error: {e}")

        # render
        window.render(grid)

        # FPS clamp
        app_core.fps_limiter.limit_fps()

    print("[demo] cleaning resources...")
    window.cleanup()
    app_core.shutdown()

    print("[demo] demo finished")

if __name__ == "__main__":
    main()
