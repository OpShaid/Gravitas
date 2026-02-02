
import pytest
import time
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gravitas.core.container import container
from gravitas.core.app import AppCore
from gravitas.compute.vector_field import vector_calculator
from plugins.marker_system import MarkerSystem


@pytest.fixture(scope="module")
def setup_performance_test():
    
    app_core = container.resolve(AppCore)
    if app_core is None or isinstance(app_core, type):
        app_core = AppCore()
        container.register_singleton(AppCore, app_core)

    # creategrid
    grid = app_core.grid_manager.init_grid(128, 128)

    marker_system = MarkerSystem(app_core)

    yield app_core, grid, marker_system

    app_core.shutdown()


def test_marker_update_performance(setup_performance_test):
    
    app_core, grid, marker_system = setup_performance_test

    marker_counts = [100, 1000, 10000]
    h, w = grid.shape[:2]

    print("\n=== markerupdateperformancetest ===")
    print(f"gridsize: {w}x{h}")

    for count in marker_counts:
        print(f"\n--- test {count} marker ---")

        marker_system.clear_markers()

        for _ in range(count):
            x = random.uniform(0, w - 1)
            y = random.uniform(0, h - 1)
            marker_system.add_marker(x, y)

        marker_positions = [(m['x'], m['y']) for m in marker_system.get_markers()]
        tiny_positions = [(m['x'], m['y'], m['mag']) for m in marker_system.get_markers()]

        start_time = time.perf_counter()
        marker_system.update_markers(grid, dt=1.0, gravity=0.01, speed_factor=0.9)
        update_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        fitted_vectors = vector_calculator.fit_vectors_at_positions_batch(grid, marker_positions)
        fit_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        vector_calculator.create_tiny_vectors_batch(grid, tiny_positions)
        tiny_time = time.perf_counter() - start_time

        print(f"update_markers time: {update_time:.4f}s")
        print(f"fit_vectors_at_positions_batch time: {fit_time:.4f}s")
        print(f"create_tiny_vectors_batch time: {tiny_time:.4f}s")
        print(f"eachmarkertime: {(update_time)/count:.6f}s")
        print(f"eachmarkerfittime: {fit_time/count:.6f}s")

    print("\n=== performancetestdone ===")
