import pytest
import numpy as np
from gravitas.compute.vector_field import VectorFieldCalculator


class TestVectorFieldCalculator:
    

    def setup_method(self):
        
        self.calculator = VectorFieldCalculator()

    def test_create_vector_grid(self):
        
        grid = self.calculator.create_vector_grid(10, 20, (1.0, 2.0))

        assert grid.shape == (20, 10, 2)  # height, width, 2
        assert np.all(grid == (1.0, 2.0))

    def test_sum_adjacent_vectors(self):
        
        grid = self.calculator.create_vector_grid(5, 5, (0.0, 0.0))
        grid[1, 1] = (1.0, 0.0)
        grid[0, 1] = (0.0, 1.0)
        grid[2, 1] = (0.0, -1.0)
        grid[1, 0] = (-1.0, 0.0)
        grid[1, 2] = (2.0, 0.0)

        vx, vy = self.calculator.sum_adjacent_vectors(grid, 1, 1)

        expected_vx = 0.0 * 1.0 + 0.25 * (0.0 + 0.0 + (-1.0) + 2.0)
        expected_vy = 0.0 * 0.0 + 0.25 * (1.0 + (-1.0) + 0.0 + 0.0)

        assert abs(vx - expected_vx) < 1e-6
        assert abs(vy - expected_vy) < 1e-6

    def test_update_grid_with_adjacent_sum(self):
        
        grid = self.calculator.create_vector_grid(3, 3, (0.0, 0.0))
        grid[1, 1] = (1.0, 1.0)

        original_grid = grid.copy()
        updated_grid = self.calculator.update_grid_with_adjacent_sum(grid)

        assert updated_grid.shape == original_grid.shape
        assert not np.array_equal(updated_grid[1, 1], original_grid[1, 1])

    def test_add_vector_at_position(self):
        
        grid = self.calculator.create_vector_grid(5, 5, (0.0, 0.0))

        self.calculator.add_vector_at_position(grid, 2.5, 2.5, 1.0, 1.0)

        affected = False
        for y in range(2, 4):
            for x in range(2, 4):
                if grid[y, x, 0] != 0.0 or grid[y, x, 1] != 0.0:
                    affected = True
                    break

        assert affected

    def test_fit_vector_at_position(self):
        
        grid = self.calculator.create_vector_grid(5, 5, (0.0, 0.0))
        grid[2, 2] = (1.0, 1.0)
        grid[2, 3] = (1.0, 0.0)
        grid[3, 2] = (0.0, 1.0)
        grid[3, 3] = (0.0, 0.0)

        vx, vy = self.calculator.fit_vector_at_position(grid, 2.5, 2.5)

        assert isinstance(vx, float)
        assert isinstance(vy, float)


if __name__ == "__main__":
    pytest.main([__file__])
