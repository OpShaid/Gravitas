import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from gravitas.compute.gpu_vector_field import GPUVectorFieldCalculator
from gravitas.core.events import EventType


class TestGPUVectorFieldCalculator:
    

    def setup_method(self):
        
        self.calculator = GPUVectorFieldCalculator()

    @patch('pyopencl.get_platforms')
    def test_init_opencl_success(self, mock_get_platforms):
        
        # Mock platform and device
        mock_platform = Mock()
        mock_device = Mock()
        mock_platform.get_devices.return_value = [mock_device]
        mock_get_platforms.return_value = [mock_platform]

        # Mock context and queue
        with patch('pyopencl.Context') as mock_context_class, \
             patch('pyopencl.CommandQueue') as mock_queue_class, \
             patch('gravitas.compute.gpu_vector_field.GPUVectorFieldCalculator._compile_programs') as mock_compile:

            mock_context = Mock()
            mock_queue = Mock()
            mock_context_class.return_value = mock_context
            mock_queue_class.return_value = mock_queue

            calculator = GPUVectorFieldCalculator()

            assert calculator._initialized == True
            assert calculator._ctx == mock_context
            assert calculator._queue == mock_queue

    @patch('pyopencl.get_platforms')
    def test_init_opencl_no_platforms(self, mock_get_platforms):
        
        mock_get_platforms.return_value = []

        calculator = GPUVectorFieldCalculator()

        assert calculator._initialized == False

    @patch('pyopencl.get_platforms')
    def test_init_opencl_no_devices(self, mock_get_platforms):
        
        mock_platform = Mock()
        mock_platform.get_devices.return_value = []
        mock_get_platforms.return_value = [mock_platform]

        calculator = GPUVectorFieldCalculator()

        assert calculator._initialized == False

    @patch('pyopencl.get_platforms')
    @patch('pyopencl.Context')
    def test_init_opencl_context_creation_failure(self, mock_context_class, mock_get_platforms):
        
        mock_platform = Mock()
        mock_device = Mock()
        mock_platform.get_devices.return_value = [mock_device]
        mock_get_platforms.return_value = [mock_platform]

        mock_context_class.side_effect = Exception("Context creation failed")

        calculator = GPUVectorFieldCalculator()

        assert calculator._initialized == False

    def test_sum_adjacent_vectors_not_initialized(self):
        
        self.calculator._initialized = False

        with pytest.raises(RuntimeError, match="GPUcomputeinitialize"):
            self.calculator.sum_adjacent_vectors(np.zeros((5, 5, 2), dtype=np.float32), 1, 1)

    def test_sum_adjacent_vectors_invalid_grid(self):
        
        self.calculator._initialized = True

        # Test None grid
        result = self.calculator.sum_adjacent_vectors(None, 1, 1)
        assert result == (0.0, 0.0)

        # Test non-numpy array - should raise TypeError
        with pytest.raises(TypeError, match="grid mustis numpy.ndarray type"):
            self.calculator.sum_adjacent_vectors([], 1, 1)

    @patch('pyopencl.Buffer')
    @patch('pyopencl.enqueue_nd_range_kernel')
    @patch('pyopencl.enqueue_copy')
    def test_sum_adjacent_vectors_success(self, mock_enqueue_copy, mock_enqueue_kernel, mock_buffer):
        
        self.calculator._initialized = True

        # Mock kernel
        mock_kernel = Mock()
        self.calculator._kernels = {'sum_adjacent_vectors': mock_kernel}

        # Mock buffers
        mock_grid_buf = Mock()
        mock_result_buf = Mock()
        mock_buffer.side_effect = [mock_grid_buf, mock_result_buf]

        # Create test grid
        grid = np.zeros((5, 5, 2), dtype=np.float32)
        grid[1, 1] = (1.0, 0.0)  # Center
        grid[0, 1] = (0.0, 1.0)  # Top
        grid[2, 1] = (0.0, -1.0)  # Bottom
        grid[1, 0] = (-1.0, 0.0)  # Left
        grid[1, 2] = (2.0, 0.0)  # Right

        # Mock result
        result = np.zeros((5, 5, 2), dtype=np.float32)
        result[1, 1] = (0.5, 0.0)  # Expected result
        mock_enqueue_copy.side_effect = lambda queue, dest, src: dest.__setitem__(slice(None), result)

        vx, vy = self.calculator.sum_adjacent_vectors(grid, 1, 1)

        assert isinstance(vx, np.floating)
        assert isinstance(vy, np.floating)
        assert abs(vx - 0.5) < 1e-6
        assert abs(vy - 0.0) < 1e-6

    def test_update_grid_with_adjacent_sum_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)

        with pytest.raises(RuntimeError, match="GPUcomputeinitialize"):
            self.calculator.update_grid_with_adjacent_sum(grid)

    def test_update_grid_with_adjacent_sum_invalid_grid(self):
        
        self.calculator._initialized = True

        # Test None grid
        result = self.calculator.update_grid_with_adjacent_sum(None)
        assert result is None

        # Test non-numpy array
        result = self.calculator.update_grid_with_adjacent_sum([])
        assert result == []

    @patch('pyopencl.Buffer')
    @patch('pyopencl.enqueue_nd_range_kernel')
    @patch('pyopencl.enqueue_copy')
    def test_update_grid_with_adjacent_sum_success(self, mock_enqueue_copy, mock_enqueue_kernel, mock_buffer):
        
        self.calculator._initialized = True

        # Mock kernel
        mock_kernel = Mock()
        self.calculator._kernels = {'update_grid_with_adjacent_sum': mock_kernel}

        # Mock buffer
        mock_grid_buf = Mock()
        mock_buffer.return_value = mock_grid_buf

        # Create test grid
        grid = np.ones((3, 3, 2), dtype=np.float32)

        # Mock the copy operation to modify grid
        def mock_copy(queue, dest, src):
            dest.fill(2.0)  # Simulate GPU processing result

        mock_enqueue_copy.side_effect = mock_copy

        result = self.calculator.update_grid_with_adjacent_sum(grid)

        assert result is grid
        assert np.all(result == 2.0)

    def test_create_vector_grid(self):
        
        grid = self.calculator.create_vector_grid(10, 20, (1.0, 2.0))

        assert grid.shape == (20, 10, 2)
        assert np.all(grid == (1.0, 2.0))

    def test_create_tiny_vector_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)

        # Should not raise exception, just return
        self.calculator.create_tiny_vector(grid, 2.0, 2.0, 1.0)

    def test_create_tiny_vector_invalid_grid(self):
        
        self.calculator._initialized = True

        # Test non-numpy array
        self.calculator.create_tiny_vector([], 2.0, 2.0, 1.0)

    def test_create_tiny_vectors_batch_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)
        positions = [(1.0, 1.0, 1.0)]

        with pytest.raises(RuntimeError, match="GPUcomputeinitialize"):
            self.calculator.create_tiny_vectors_batch(grid, positions)

    def test_create_tiny_vectors_batch_invalid_input(self):
        
        self.calculator._initialized = True

        # Test None grid
        self.calculator.create_tiny_vectors_batch(None, [(1.0, 1.0, 1.0)])

        # Test empty positions
        grid = np.zeros((5, 5, 2), dtype=np.float32)
        self.calculator.create_tiny_vectors_batch(grid, [])

        # Test non-numpy grid
        self.calculator.create_tiny_vectors_batch([], [(1.0, 1.0, 1.0)])

    @patch('pyopencl.Buffer')
    @patch('pyopencl.enqueue_nd_range_kernel')
    @patch('pyopencl.enqueue_copy')
    def test_create_tiny_vectors_batch_success(self, mock_enqueue_copy, mock_enqueue_kernel, mock_buffer):
        
        self.calculator._initialized = True

        # Mock kernel
        mock_kernel = Mock()
        self.calculator._kernels = {'create_tiny_vectors_batch': mock_kernel}

        # Mock buffers
        mock_temp_buf = Mock()
        mock_pos_buf = Mock()
        mock_buffer.side_effect = [mock_temp_buf, mock_pos_buf]

        # Create test data
        grid = np.zeros((5, 5, 2), dtype=np.float32)
        positions = [(2.0, 2.0, 1.0)]

        # Mock result
        temp_grid_flat = np.ones(50, dtype=np.float32)  # 5*5*2 = 50
        mock_enqueue_copy.side_effect = lambda queue, dest, src: dest.__setitem__(slice(None), temp_grid_flat)

        self.calculator.create_tiny_vectors_batch(grid, positions)

        # Grid should be modified
        assert not np.all(grid == 0.0)

    def test_add_vector_at_position_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)

        # Should not raise exception
        self.calculator.add_vector_at_position(grid, 2.0, 2.0, 1.0, 1.0)

    def test_add_vector_at_position_invalid_grid(self):
        
        self.calculator._initialized = True

        # Test non-numpy array
        self.calculator.add_vector_at_position([], 2.0, 2.0, 1.0, 1.0)

        # Test wrong dimensions
        self.calculator.add_vector_at_position(np.zeros((5, 5)), 2.0, 2.0, 1.0, 1.0)

    def test_add_vector_at_position_success(self):
        
        self.calculator._initialized = True

        grid = np.zeros((5, 5, 2), dtype=np.float32)

        self.calculator.add_vector_at_position(grid, 2.0, 2.0, 1.0, 1.0)

        # Check that vectors were added at interpolated positions
        assert not np.all(grid == 0.0)

    def test_fit_vector_at_position_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)

        with pytest.raises(RuntimeError, match="GPUcomputeinitialize"):
            self.calculator.fit_vector_at_position(grid, 2.0, 2.0)

    def test_fit_vector_at_position_invalid_grid(self):
        
        self.calculator._initialized = True

        # Test None grid
        result = self.calculator.fit_vector_at_position(None, 2.0, 2.0)
        assert result == (0.0, 0.0)

        # Test non-numpy array
        result = self.calculator.fit_vector_at_position([], 2.0, 2.0)
        assert result == (0.0, 0.0)

        # Test wrong dimensions
        result = self.calculator.fit_vector_at_position(np.zeros((5, 5)), 2.0, 2.0)
        assert result == (0.0, 0.0)

    def test_fit_vector_at_position_success(self):
        
        self.calculator._initialized = True

        grid = np.zeros((5, 5, 2), dtype=np.float32)
        grid[2, 2] = (1.0, 1.0)

        vx, vy = self.calculator.fit_vector_at_position(grid, 2.0, 2.0)

        assert isinstance(vx, float)
        assert isinstance(vy, float)
        assert abs(vx - 1.0) < 1e-6
        assert abs(vy - 1.0) < 1e-6

    def test_fit_vectors_at_positions_batch_not_initialized(self):
        
        self.calculator._initialized = False

        grid = np.zeros((5, 5, 2), dtype=np.float32)
        positions = [(2.0, 2.0)]

        with pytest.raises(RuntimeError, match="GPUcomputeinitialize"):
            self.calculator.fit_vectors_at_positions_batch(grid, positions)

    def test_fit_vectors_at_positions_batch_invalid_input(self):
        
        self.calculator._initialized = True

        # Test None grid
        result = self.calculator.fit_vectors_at_positions_batch(None, [(2.0, 2.0)])
        assert result == [(0.0, 0.0)]

        # Test empty positions
        grid = np.zeros((5, 5, 2), dtype=np.float32)
        result = self.calculator.fit_vectors_at_positions_batch(grid, [])
        assert result == []

        # Test non-numpy grid
        result = self.calculator.fit_vectors_at_positions_batch([], [(2.0, 2.0)])
        assert result == [(0.0, 0.0)]

    @patch('pyopencl.Buffer')
    @patch('pyopencl.enqueue_nd_range_kernel')
    @patch('pyopencl.enqueue_copy')
    def test_fit_vectors_at_positions_batch_success(self, mock_enqueue_copy, mock_enqueue_kernel, mock_buffer):
        
        self.calculator._initialized = True

        # Mock kernel
        mock_kernel = Mock()
        self.calculator._kernels = {'fit_vectors_at_positions_batch': mock_kernel}

        # Mock buffers
        mock_grid_buf = Mock()
        mock_pos_buf = Mock()
        mock_results_buf = Mock()
        mock_buffer.side_effect = [mock_grid_buf, mock_pos_buf, mock_results_buf]

        # Create test data
        grid = np.zeros((5, 5, 2), dtype=np.float32)
        grid[2, 2] = (1.0, 1.0)
        positions = [(2.0, 2.0)]

        # Mock result
        results = np.array([[1.0, 1.0]], dtype=np.float32)
        mock_enqueue_copy.side_effect = lambda queue, dest, src: dest.__setitem__(slice(None), results)

        result = self.calculator.fit_vectors_at_positions_batch(grid, positions)

        assert len(result) == 1
        assert result[0] == (1.0, 1.0)

    def test_cleanup(self):
        
        # Set up mock objects
        self.calculator._ctx = Mock()
        self.calculator._queue = Mock()
        self.calculator._programs = {'test': Mock()}
        self.calculator._kernels = {'test': Mock()}
        self.calculator._initialized = True

        self.calculator.cleanup()

        # After cleanup, attributes should be cleared
        assert not hasattr(self.calculator, '_ctx') or self.calculator._ctx is None
        assert not hasattr(self.calculator, '_queue') or self.calculator._queue is None
        assert self.calculator._programs == {}
        assert self.calculator._kernels == {}
        assert not self.calculator._initialized


if __name__ == "__main__":
    pytest.main([__file__])
