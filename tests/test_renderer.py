import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from gravitas.graphics.renderer import VectorFieldRenderer, ShaderProgram, vector_field_renderer
from gravitas.core.events import EventType, event_bus
from gravitas.core.state import state_manager

# Mock OpenGL constants and functions
GL_LINES = 1
GL_POINTS = 0
GL_COLOR_BUFFER_BIT = 16384
GL_DEPTH_BUFFER_BIT = 256


class TestShaderProgram:
    

    def setup_method(self):
        
        self.vertex_src = 
        mock_compile_program.return_value = 1
        mock_compile_shader.return_value = 2

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader.compile()

        assert shader._program == 1
        mock_compile_shader.assert_called()
        mock_compile_program.assert_called_once_with(2, 2)

    @patch('OpenGL.GL.shaders.compileShader')
    def test_compile_failure(self, mock_compile_shader):
        
        mock_compile_shader.side_effect = Exception("Compile error")

        shader = ShaderProgram(self.vertex_src, self.fragment_src)

        with pytest.raises(Exception):
            shader.compile()

    @patch('gravitas.graphics.renderer.glUseProgram')
    def test_use_program(self, mock_use_program):
        
        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.use()

        mock_use_program.assert_called_once_with(1)

    @patch('gravitas.graphics.renderer.glGetUniformLocation')
    def test_get_uniform_location(self, mock_get_uniform):
        
        mock_get_uniform.return_value = 5

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        loc = shader.get_uniform_location("test_uniform")

        assert loc == 5
        mock_get_uniform.assert_called_once_with(1, "test_uniform")

        loc2 = shader.get_uniform_location("test_uniform")
        assert loc2 == 5
        mock_get_uniform.assert_called_once()

    @patch('gravitas.graphics.renderer.glGetAttribLocation')
    def test_get_attribute_location(self, mock_get_attrib):
        
        mock_get_attrib.return_value = 3

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        loc = shader.get_attribute_location("test_attr")

        assert loc == 3
        mock_get_attrib.assert_called_once_with(1, "test_attr")

    @patch('gravitas.graphics.renderer.glUniform1f')
    @patch('gravitas.graphics.renderer.glGetUniformLocation')
    def test_set_uniform_float(self, mock_get_uniform, mock_uniform1f):
        
        mock_get_uniform.return_value = 5

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.set_uniform_float("test_float", 3.14)

        mock_uniform1f.assert_called_once_with(5, 3.14)

    @patch('gravitas.graphics.renderer.glUniform2f')
    @patch('gravitas.graphics.renderer.glGetUniformLocation')
    def test_set_uniform_vec2(self, mock_get_uniform, mock_uniform2f):
        
        mock_get_uniform.return_value = 5

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.set_uniform_vec2("test_vec2", (1.0, 2.0))

        mock_uniform2f.assert_called_once_with(5, 1.0, 2.0)

    @patch('gravitas.graphics.renderer.glUniform3f')
    @patch('gravitas.graphics.renderer.glGetUniformLocation')
    def test_set_uniform_vec3(self, mock_get_uniform, mock_uniform3f):
        
        mock_get_uniform.return_value = 5

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.set_uniform_vec3("test_vec3", (1.0, 2.0, 3.0))

        mock_uniform3f.assert_called_once_with(5, 1.0, 2.0, 3.0)

    @patch('gravitas.graphics.renderer.glGetString')
    @patch('gravitas.graphics.renderer.glDeleteProgram')
    def test_cleanup_with_context(self, mock_delete_program, mock_get_string):
        
        mock_get_string.return_value = b"OpenGL 3.3"

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.cleanup()

        mock_delete_program.assert_called_once_with(1)
        assert shader._program is None

    @patch('gravitas.graphics.renderer.glGetString')
    def test_cleanup_without_context(self, mock_get_string):
        
        mock_get_string.side_effect = Exception("No context")

        shader = ShaderProgram(self.vertex_src, self.fragment_src)
        shader._program = 1

        shader.cleanup()

        assert shader._program is None


class TestVectorFieldRenderer:
    

    def setup_method(self):
        
        self.renderer = VectorFieldRenderer()

    @patch('gravitas.graphics.renderer.glGenVertexArrays')
    @patch('gravitas.graphics.renderer.glGenBuffers')
    @patch('gravitas.graphics.renderer.ShaderProgram.compile')
    def test_initialize_success(self, mock_compile, mock_gen_buffers, mock_gen_vertex_arrays):
        
        mock_gen_vertex_arrays.return_value = 1
        mock_gen_buffers.return_value = 2

        self.renderer.initialize()

        assert self.renderer._initialized
        assert self.renderer._vao == 1
        assert self.renderer._vbo == 2
        mock_compile.assert_called_once()

    @patch('gravitas.graphics.renderer.ShaderProgram.compile')
    def test_initialize_failure(self, mock_compile):
        
        mock_compile.side_effect = Exception("Compile failed")

        with pytest.raises(Exception):
            self.renderer.initialize()

        assert not self.renderer._initialized

    @patch('gravitas.graphics.renderer.glLineWidth')
    @patch('gravitas.graphics.renderer.glUseProgram')
    @patch('gravitas.graphics.renderer.glBindVertexArray')
    @patch('gravitas.graphics.renderer.glBindBuffer')
    @patch('gravitas.graphics.renderer.glBufferData')
    @patch('gravitas.graphics.renderer.glEnableVertexAttribArray')
    @patch('gravitas.graphics.renderer.glVertexAttribPointer')
    @patch('gravitas.graphics.renderer.glDrawArrays')
    @patch('gravitas.graphics.renderer.ShaderProgram.get_attribute_location')
    @patch('gravitas.graphics.renderer.ShaderProgram.set_uniform_vec2')
    def test_render_vector_field_empty_grid(self, mock_set_uniform, mock_get_attr,
                                           mock_draw_arrays, mock_vertex_attrib, mock_enable_attr,
                                           mock_buffer_data, mock_bind_buffer, mock_bind_vao,
                                           mock_use_program, mock_line_width):
        
        grid = np.zeros((10, 10, 2), dtype=np.float32)

        self.renderer._initialized = True
        self.renderer.render_vector_field(grid)

        mock_draw_arrays.assert_not_called()

    @patch('gravitas.graphics.renderer.glLineWidth')
    @patch('gravitas.graphics.renderer.glUseProgram')
    @patch('gravitas.graphics.renderer.glBindVertexArray')
    @patch('gravitas.graphics.renderer.glBindBuffer')
    @patch('gravitas.graphics.renderer.glBufferData')
    @patch('gravitas.graphics.renderer.glEnableVertexAttribArray')
    @patch('gravitas.graphics.renderer.glVertexAttribPointer')
    @patch('gravitas.graphics.renderer.glDrawArrays')
    @patch('gravitas.graphics.renderer.ShaderProgram.get_attribute_location')
    @patch('gravitas.graphics.renderer.ShaderProgram.set_uniform_vec2')
    def test_render_vector_field_with_vectors(self, mock_set_uniform, mock_get_attr,
                                             mock_draw_arrays, mock_vertex_attrib, mock_enable_attr,
                                             mock_buffer_data, mock_bind_buffer, mock_bind_vao,
                                             mock_use_program, mock_line_width):
        
        grid = np.zeros((3, 3, 2), dtype=np.float32)
        grid[1, 1] = (1.0, 1.0)

        mock_get_attr.return_value = 0

        self.renderer._initialized = True
        self.renderer.render_vector_field(grid)

        mock_draw_arrays.assert_called_once_with(GL_LINES, 0, 2)

    @patch('gravitas.graphics.renderer.glClearColor')
    @patch('gravitas.graphics.renderer.glClear')
    def test_render_background(self, mock_clear, mock_clear_color):
        
        self.renderer.render_background()

        mock_clear_color.assert_called_once()
        mock_clear.assert_called_once_with(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    @patch('gravitas.graphics.renderer.glPointSize')
    @patch('gravitas.graphics.renderer.glUseProgram')
    @patch('gravitas.graphics.renderer.glBindVertexArray')
    @patch('gravitas.graphics.renderer.glBindBuffer')
    @patch('gravitas.graphics.renderer.glBufferData')
    @patch('gravitas.graphics.renderer.glEnableVertexAttribArray')
    @patch('gravitas.graphics.renderer.glVertexAttribPointer')
    @patch('gravitas.graphics.renderer.glDrawArrays')
    @patch('gravitas.graphics.renderer.ShaderProgram.get_attribute_location')
    @patch('gravitas.graphics.renderer.ShaderProgram.set_uniform_vec2')
    def test_render_markers(self, mock_set_uniform, mock_get_attr,
                           mock_draw_arrays, mock_vertex_attrib, mock_enable_attr,
                           mock_buffer_data, mock_bind_buffer, mock_bind_vao,
                           mock_use_program, mock_point_size):
        
        markers = [{"x": 1.0, "y": 2.0}, {"x": 3.0, "y": 4.0}]
        self.renderer._state_manager.set("markers", markers)

        mock_get_attr.return_value = 0

        self.renderer._initialized = True
        self.renderer.render_markers()

        mock_draw_arrays.assert_called_once_with(GL_POINTS, 0, 2)
        mock_point_size.assert_called_once()

    @patch('gravitas.graphics.renderer.glDeleteVertexArrays')
    @patch('gravitas.graphics.renderer.glDeleteBuffers')
    @patch('gravitas.graphics.renderer.glGetString')
    def test_cleanup(self, mock_get_string, mock_delete_buffers, mock_delete_vertex_arrays):
        
        mock_get_string.return_value = b"OpenGL 3.3"

        self.renderer._initialized = True
        self.renderer._vao = 1
        self.renderer._vbo = 2
        self.renderer._grid_vao = 3
        self.renderer._grid_vbo = 4

        self.renderer.cleanup()

        assert not self.renderer._initialized
        assert self.renderer._vao is None
        assert self.renderer._vbo is None
        assert self.renderer._grid_vao is None
        assert self.renderer._grid_vbo is None

    def test_handle_app_initialized(self):
        
        event = Mock()
        event.type = EventType.APP_INITIALIZED

        self.renderer.handle(event)


class TestGlobalRenderer:
    

    def test_global_renderer_exists(self):
        
        assert vector_field_renderer is not None
        assert isinstance(vector_field_renderer, VectorFieldRenderer)


if __name__ == "__main__":
    pytest.main([__file__])
