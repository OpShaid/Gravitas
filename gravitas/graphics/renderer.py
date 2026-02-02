
import numpy as np
import ctypes
from typing import Optional, Dict, Any, List, Tuple
from OpenGL.GL import *
from OpenGL.GL import shaders
from ..core.events import Event, EventType, event_bus, EventHandler
from ..core.state import state_manager

class ShaderProgram:
    
    def __init__(self, vertex_src: str, fragment_src: str):
        self._program = None
        self._uniform_locations = {}
        self._attribute_locations = {}
        self._vertex_src = vertex_src
        self._fragment_src = fragment_src

    def compile(self) -> None:
        
        try:
            vertex_shader = shaders.compileShader(self._vertex_src, GL_VERTEX_SHADER)

            fragment_shader = shaders.compileShader(self._fragment_src, GL_FRAGMENT_SHADER)

            self._program = shaders.compileProgram(vertex_shader, fragment_shader)

            print("[render] shaderprogramcompilesuccess")
        except Exception as e:
            print(f"[render] shadercompileerror: {e}")
            raise

    def use(self) -> None:
        
        if self._program is not None:
            glUseProgram(self._program)

    def get_uniform_location(self, name: str) -> int:
        
        if name not in self._uniform_locations:
            self._uniform_locations[name] = glGetUniformLocation(self._program, name)
        return self._uniform_locations[name]

    def get_attribute_location(self, name: str) -> int:
        
        if name not in self._attribute_locations:
            self._attribute_locations[name] = glGetAttribLocation(self._program, name)
        return self._attribute_locations[name]

    def set_uniform_float(self, name: str, value: float) -> None:
        
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform1f(loc, value)

    def set_uniform_vec2(self, name: str, value: Tuple[float, float]) -> None:
        
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform2f(loc, value[0], value[1])

    def set_uniform_vec3(self, name: str, value: Tuple[float, float, float]) -> None:
        
        loc = self.get_uniform_location(name)
        if loc >= 0:
            glUniform3f(loc, value[0], value[1], value[2])

    def cleanup(self) -> None:
        
        if self._program is not None:
            if callable(glGetString) and callable(glDeleteProgram):
                try:
                    glGetString(GL_VERSION)
                    glDeleteProgram(self._program)
                except:
                    pass
            self._program = None
            self._uniform_locations.clear()
            self._attribute_locations.clear()

class VectorFieldRenderer(EventHandler):
    
    def __init__(self):
        self._event_bus = event_bus
        self._state_manager = state_manager

        self._vertex_shader_src = initializerenderrendervector fieldrendergridrenderbackgroundrenderin state_manager middleregistermarker（point）checkOpenGLcontextisnovalid
        if buffer_id is not None and self._is_opengl_context_valid():
            try:
                delete_func(1, [buffer_id])
            except Exception as e:
                print(f"[render] deletebufferobjectfail: {e}")

    def cleanup(self) -> None:
        
        if not self._initialized:
            return

        try:
            self._shader_program.cleanup()

            self._safe_delete_buffer(self._vao, glDeleteVertexArrays)
            self._safe_delete_buffer(self._vbo, glDeleteBuffers)
            self._safe_delete_buffer(self._grid_vao, glDeleteVertexArrays)
            self._safe_delete_buffer(self._grid_vbo, glDeleteBuffers)

            self._vao = None
            self._vbo = None
            self._grid_vao = None
            self._grid_vbo = None

            self._initialized = False
            print("[render] resourcedone")
        except Exception as e:
            print(f"[render] cleaning resourceshour: {e}")

    def handle(self, event: Event) -> None:
        
        if event.type == EventType.APP_INITIALIZED:
            pass

vector_field_renderer = VectorFieldRenderer()

def render_vector_field(grid: np.ndarray, cell_size: float = 1.0,
                       cam_x: float = 0.0, cam_y: float = 0.0, cam_zoom: float = 1.0,
                       viewport_width: int = 800, viewport_height: int = 600) -> None:
    
    vector_field_renderer.render_vector_field(grid, cell_size, cam_x, cam_y, cam_zoom, viewport_width, viewport_height)

def render_grid(grid: np.ndarray, cell_size: float = 1.0,
               cam_x: float = 0.0, cam_y: float = 0.0, cam_zoom: float = 1.0,
               viewport_width: int = 800, viewport_height: int = 600) -> None:
    
    vector_field_renderer.render_grid(grid, cell_size, cam_x, cam_y, cam_zoom, viewport_width, viewport_height)

def render_background() -> None:
    
    vector_field_renderer.render_background()
