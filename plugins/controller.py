
from typing import Tuple
import numpy as np
from gravitas.input import input_handler


class Controller:
    def __init__(self, app_core, vector_calculator, marker_system, grid: np.ndarray):
        self.app_core = app_core
        self.vector_calculator = vector_calculator
        self.marker_system = marker_system
        self.grid = grid

        self.vector_field_direction = True

    def _screen_to_grid(self, mx: float, my: float) -> Tuple[float, float]:
        
        cam_x = self.app_core.state_manager.get("cam_x", 0.0)
        cam_y = self.app_core.state_manager.get("cam_y", 0.0)
        cam_zoom = self.app_core.state_manager.get("cam_zoom", 1.0)
        viewport_width = self.app_core.state_manager.get("viewport_width", 800)
        viewport_height = self.app_core.state_manager.get("viewport_height", 600)
        cell_size = self.app_core.state_manager.get("cell_size", 1.0)

        world_x = cam_x + (mx - (viewport_width / 2.0)) / cam_zoom
        world_y = cam_y + (my - (viewport_height / 2.0)) / cam_zoom

        gx = world_x / cell_size
        gy = world_y / cell_size

        return gx, gy

    def reset_view(self):
        
        try:
            self.app_core.view_manager.reset_view(self.grid.shape[1], self.grid.shape[0])
        except Exception as e:
            print(f"[error] reset_view exception: {e}")

    def toggle_grid(self):
        
        show_grid = self.app_core.state_manager.get("show_grid", True)
        self.app_core.state_manager.set("show_grid", not show_grid)

    def clear_grid(self):
        
        try:
            self.grid.fill(0.0)
        except Exception as e:
            print(f"[error] clear_grid exception: {e}")

    def switch_vector_field_direction(self):
        
        try:
            self.vector_field_direction = not self.vector_field_direction
            direction = "outward" if self.vector_field_direction else "inward"
            print(f"[demo] vector fielddirectiontoggleas: {direction}")
        except Exception as e:
            print(f"[error] togglevector fielddirection exception: {e}")

    def add_marker(self, x: float, y: float, mag: float = 1.0):
        
        try:
            self.marker_system.add_marker(float(x), float(y), float(mag))
            print(f"[controller] addmarker: position({x}, {y}), magnitudevalue{mag}")
        except Exception as e:
            print(f"[error] addmarkerexception: {e}")

    def clear_markers(self):
        
        try:
            self.marker_system.clear_markers()
            print("[controller] clearedallmarker")
        except Exception as e:
            print(f"[error] clearmarkerexception: {e}")

    def set_compute_device(self, device: str):
        
        try:
            if device.lower() not in ["cpu", "gpu"]:
                print(f"[error] invaliddevicetype: {device}，as 'cpu' or 'gpu'")
                return
            success = self.vector_calculator.set_device(device.lower())
            if success:
                print(f"[controller] computedevicesetas: {device.upper()}")
            else:
                print(f"[error] setasdevice: {device.upper()}")
        except Exception as e:
            print(f"[error] setcomputedeviceexception: {e}")

    def set_gravity(self, value: float):
        
        try:
            self.app_core.state_manager.set("gravity", float(value))
            print(f"[controller] gravityvelocitysetas: {value}")
        except Exception as e:
            print(f"[error] setgravityexception: {e}")

    def set_speed_factor(self, value: float):
        
        try:
            self.app_core.state_manager.set("speed_factor", float(value))
            print(f"[controller] velocitysetas: {value}")
        except Exception as e:
            print(f"[error] setvelocityexception: {e}")

    def place_vector_field(self, mx: float, my: float):
        
        try:
            gx, gy = self._screen_to_grid(mx, my)

            h, w = self.grid.shape[:2]
            if gx < 0 or gx >= w or gy < 0 or gy >= h:
                print(f"[demo] clickpositiongrid: ({gx}, {gy})")
                return

            mag = 1.0
            magnitude = mag if self.vector_field_direction else -mag

            self.marker_system.add_marker(gx, gy, float(magnitude))

            self.app_core.state_manager.update({"view_changed": True, "grid_updated": True})
        except Exception as e:
            print(f"[error] handlerfkeypressedhourexception: {e}")

    def handle_mouse_left_press(self, mx: float, my: float) -> dict:
        
        try:
            gx, gy = self._screen_to_grid(mx, my)

            h, w = self.grid.shape[:2]
            if gx < 0 or gx >= w or gy < 0 or gy >= h:
                print(f"[demo] clickpositiongrid: ({gx}, {gy})")
                return None

            markers = self.marker_system.get_markers()
            if not markers:
                print("[demo] noneavailablemarker")
                return None

            min_dist = float('inf')
            closest_marker = None
            threshold = 5.0
            for marker in markers:
                marker_x = marker["x"]
                marker_y = marker["y"]
                dist = ((marker_x - gx) ** 2 + (marker_y - gy) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_marker = marker

            if closest_marker is None or min_dist > threshold:
                print("[demo] not foundmarkerorselectvalue")
                return None

            return closest_marker
        except Exception as e:
            print(f"[error] handlermouseleftkeypressedhourexception: {e}")
            return None

    def handle_mouse_drag(self, mx: float, my: float, selected_marker: dict):
        
        if selected_marker is None:
            return

        try:
            gx, gy = self._screen_to_grid(mx, my)

            h, w = self.grid.shape[:2]
            if gx >= 0 and gx < w and gy >= 0 and gy < h:
                vx = gx - selected_marker["x"]
                vy = gy - selected_marker["y"]

                vx *= 0.1
                vy *= 0.1
                self.marker_system.add_vector_at_position(self.grid, x=selected_marker["x"], y=selected_marker["y"], vx=vx, vy=vy)

                self.app_core.state_manager.update({"view_changed": True, "grid_updated": True})
        except Exception as e:
            print(f"[error] handlerleftkeyheld downhourexception: {e}")

    def handle_mouse_drag_view(self, dx: float, dy: float):
        
        try:
            cam_zoom = self.app_core.state_manager.get("cam_zoom", 1.0)

            world_dx = dx / cam_zoom
            world_dy = dy / cam_zoom

            cam_x = self.app_core.state_manager.get("cam_x", 0.0) - world_dx
            cam_y = self.app_core.state_manager.get("cam_y", 0.0) - world_dy

            self.app_core.state_manager.update({
                "cam_x": cam_x,
                "cam_y": cam_y,
                "view_changed": True
            })
        except Exception as e:
            print(f"[error] handlergraphdrag exception: {e}")

    def handle_scroll_zoom(self, scroll_y: float):
        
        try:
            cam_zoom = self.app_core.state_manager.get("cam_zoom", 1.0)
            zoom_speed = 0.5
            zoom_min = 0.1
            zoom_max = 10.0
            cam_zoom += scroll_y * zoom_speed
            cam_zoom = max(zoom_min, min(zoom_max, cam_zoom))

            self.app_core.state_manager.update({
                "cam_zoom": cam_zoom,
                "view_changed": True
            })
        except Exception as e:
            print(f"[error] handlerscrollzoom exception: {e}")

