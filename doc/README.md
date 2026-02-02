
# Gravitas API Documentation

## Project Overview

Gravitas is a modern vector field visualization engine with a modular architecture design, providing high-performance vector field computation and rendering capabilities. By simulating physical force fields (such as electromagnetic forces), Gravitas can efficiently handle force calculations between entities, avoiding the performance bottleneck of traditional collision detection.

## Core Features

- **High-Performance Computing**: Supports CPU and GPU accelerated computation, suitable for large-scale vector field simulation
- **Modular Architecture**: Uses dependency injection, event-driven, and state management design patterns
- **Flexible Plugin System**: Supports custom computation modes, rendering effects, and user interaction
- **Real-time Visualization**: High-efficiency OpenGL-based rendering with interactive operations
- **Easy to Extend**: Clear API interfaces for developers to add new features

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from gravitas.compute.vector_field import vector_calculator

# Create vector grid
grid = vector_calculator.create_vector_grid(width=640, height=480)

# Update vector field
updated_grid = vector_calculator.update_grid_with_adjacent_sum(grid)

# Add vector influence
vector_calculator.add_vector_at_position(grid, 320.0, 240.0, 1.0, 0.5)

# Get position vector
vx, vy = vector_calculator.fit_vector_at_position(grid, 320.0, 240.0)
```

### Error Handling

```python
try:
    grid = vector_calculator.create_vector_grid(width=640, height=480)
    if grid is None:
        raise ValueError("Failed to create vector grid")
except Exception as e:
    print(f"Error: {e}")
```

## Architecture Overview

Gravitas uses a layered architecture design with the following main modules:

### Core Layer (core/)

Responsible for application lifecycle management and inter-module coordination:

- **AppCore**: Application core, integrating all managers
- **Container**: Dependency injection container
- **EventBus**: Event system with async processing and event filtering
- **StateManager**: State management with change notifications and snapshots
- **ConfigManager**: Configuration management with file loading and hot updates
- **PluginManager**: Plugin management

### Compute Layer (compute/)

Provides vector field computation functionality:

- **VectorFieldCalculator**: Main computation interface with CPU/GPU switching
- **CPUVectorFieldCalculator**: CPU implementation
- **GPUVectorFieldCalculator**: GPU implementation (OpenCL-based)

### Rendering Layer (graphics/)

Handles visual rendering:

- **VectorFieldRenderer**: Vector field renderer
- **ShaderProgram**: Shader program management

### Window Layer (window/)

Manages windows and input:

- **Window**: GLFW window management
- **InputHandler**: Input event processing

### Plugin Layer (plugins/)

Extended functionality:

- **MarkerSystem**: Marker system
- **UI**: User interface plugin
- **Command**: Command system
- **Controller**: Controller plugin

## API Reference

### VectorFieldCalculator

Main interface for vector field calculator with automatic CPU/GPU switching.

#### Properties

##### current_device: str

Get the current computation device.

**Returns:** "cpu" or "gpu"

#### Methods

##### create_vector_grid(width: int, height: int, default: Tuple[float, float] = (0, 0)) -> np.ndarray

Create a vector grid of specified size.

**Parameters:**
- `width` (int): Grid width
- `height` (int): Grid height
- `default` (Tuple[float, float]): Default vector value, defaults to (0, 0)

**Returns:** numpy array with shape (height, width, 2)

**Example:**
```python
grid = vector_calculator.create_vector_grid(640, 480, (0.0, 0.0))
```

##### update_grid_with_adjacent_sum(grid: np.ndarray) -> np.ndarray

Update the entire grid based on adjacent vectors using configured weight parameters.

**Parameters:**
- `grid` (np.ndarray): Input grid, must be a valid numpy array

**Returns:** Updated grid

**Raises:** TypeError if grid is not a numpy array

**Example:**
```python
updated_grid = vector_calculator.update_grid_with_adjacent_sum(grid)
```

##### sum_adjacent_vectors(grid: np.ndarray, x: int, y: int) -> Tuple[float, float]

Calculate the sum of vectors in four adjacent directions at a specified position.

**Parameters:**
- `grid` (np.ndarray): Input grid
- `x` (int): X coordinate (integer)
- `y` (int): Y coordinate (integer)

**Returns:** Sum of adjacent vectors (sum_x, sum_y)

##### add_vector_at_position(grid: np.ndarray, x: float, y: float, vx: float, vy: float) -> None

Add a vector at specified floating-point coordinates, distributed to adjacent integer coordinates using bilinear interpolation.

**Parameters:**
- `grid` (np.ndarray): Target grid
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `vx` (float): X component
- `vy` (float): Y component

##### fit_vector_at_position(grid: np.ndarray, x: float, y: float) -> Tuple[float, float]

Fit vector value at specified floating-point coordinates using bilinear interpolation.

**Parameters:**
- `grid` (np.ndarray): Input grid
- `x` (float): X coordinate
- `y` (float): Y coordinate

**Returns:** Interpolated vector (vx, vy)

##### create_tiny_vector(grid: np.ndarray, x: float, y: float, mag: float = 1.0) -> None

Create a tiny vector field influence at specified position, only affecting the position itself and its four neighbors.

**Parameters:**
- `grid` (np.ndarray): Target grid
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `mag` (float): Vector magnitude, defaults to 1.0

##### create_tiny_vectors_batch(grid: np.ndarray, positions: List[Tuple[float, float, float]]) -> None

Batch create tiny vector influences for performance optimization.

**Parameters:**
- `grid` (np.ndarray): Vector field grid
- `positions` (List[Tuple[float, float, float]]): Position list, each element is (x, y, mag) tuple

##### fit_vectors_at_positions_batch(grid: np.ndarray, positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]

Batch fit vector values at multiple positions.

**Parameters:**
- `grid` (np.ndarray): Vector field grid
- `positions` (List[Tuple[float, float]]): Position list, each element is (x, y) tuple

**Returns:** Vector list, each element is (vx, vy) tuple

##### set_device(device: str) -> bool

Set computation device with runtime switching support.

**Parameters:**
- `device` (str): "cpu" or "gpu"

**Returns:** Whether setting was successful

**Example:**
```python
success = vector_calculator.set_device("gpu")
if not success:
    print("GPU not available, using CPU")
```

##### cleanup() -> None

Clean up computation resources, release GPU memory, etc.

### ConfigManager

Configuration manager with file loading, hot updates, and type validation.

#### Methods

##### get(key: str, default: Any = None) -> Any

Get configuration value with dot-separated nested access support.

**Parameters:**
- `key` (str): Configuration key, supports dot separation (e.g., "grid.width")
- `default` (Any): Default value

**Returns:** Configuration value

**Example:**
```python
width = config_manager.get("grid_width", 640)
# Or use nested access
width = config_manager.get("grid.width", 640)
```

##### set(key: str, value: Any) -> bool

Set configuration value with type validation and range checking.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): Configuration value

**Returns:** Whether setting was successful

**Example:**
```python
config_manager.set("vector_scale", 1.5)
```

##### register_option(key: str, default: Any, description: str = "", type: str = "string", options: List[Any] = None, min_value: Union[int, float] = None, max_value: Union[int, float] = None) -> None

Register configuration option.

**Parameters:**
- `key` (str): Configuration key
- `default` (Any): Default value
- `description` (str): Description
- `type` (str): Type ("string", "number", "boolean", "array", "object")
- `options` (List[Any]): Optional value list
- `min_value` (Union[int, float]): Minimum value
- `max_value` (Union[int, float]): Maximum value

##### load_from_file(file_path: str) -> bool

Load configuration from file.

**Parameters:**
- `file_path` (str): Configuration file path

**Returns:** Whether loading was successful

##### save_to_file(file_path: Optional[str] = None) -> bool

Save configuration to file.

**Parameters:**
- `file_path` (Optional[str]): File path, defaults to initialization path

**Returns:** Whether saving was successful

##### reset_to_default(key: Optional[str] = None) -> None

Reset configuration to default values.

**Parameters:**
- `key` (Optional[str]): Specified key, resets all when None

##### get_all_option_info() -> Dict[str, Dict[str, Any]]

Get all configuration option information.

**Returns:** Configuration option information dictionary

### StateManager

State manager with change notifications and snapshots.

#### Methods

##### get(key: str, default: Any = None) -> Any

Get state value.

**Parameters:**
- `key` (str): State key
- `default` (Any): Default value

**Returns:** State value

##### set(key: str, value: Any, notify: bool = True) -> None

Set state value and trigger change notification.

**Parameters:**
- `key` (str): State key
- `value` (Any): State value
- `notify` (bool): Whether to notify listeners, defaults to True

##### update(updates: Dict[str, Any], notify: bool = True) -> None

Batch update state.

**Parameters:**
- `updates` (Dict[str, Any]): Update dictionary
- `notify` (bool): Whether to notify, defaults to True

##### remove(key: str) -> bool

Remove state.

**Parameters:**
- `key` (str): State key

**Returns:** Whether removal was successful

##### clear() -> None

Clear all state.

##### add_listener(key: str, callback: Callable[[str, Any, Any], None]) -> None

Add state change listener.

**Parameters:**
- `key` (str): State key
- `callback` (Callable): Callback function with parameters (key, old_value, new_value)

##### remove_listener(key: str, callback: Callable[[str, Any, Any], None]) -> None

Remove state change listener.

##### get_change_history(key: Optional[str] = None, limit: Optional[int] = None) -> List[StateChange]

Get change history.

**Parameters:**
- `key` (Optional[str]): Specified key, gets all when None
- `limit` (Optional[int]): Limit count

**Returns:** Change history list

##### create_snapshot() -> Dict[str, Any]

Create state snapshot.

**Returns:** Snapshot dictionary

##### restore_snapshot(snapshot: Dict[str, Any]) -> None

Restore state from snapshot.

**Parameters:**
- `snapshot` (Dict[str, Any]): Snapshot dictionary

### EventBus

Event system with async processing and event filtering.

#### Methods

##### subscribe(event_type: EventType, handler: EventHandler, filter: Optional[EventFilter] = None) -> None

Subscribe to event.

**Parameters:**
- `event_type` (EventType): Event type
- `handler` (EventHandler): Event handler
- `filter` (Optional[EventFilter]): Event filter

##### unsubscribe(event_type: EventType, handler: EventHandler) -> None

Unsubscribe from event.

**Parameters:**
- `event_type` (EventType): Event type
- `handler` (EventHandler): Event handler

##### publish(event: Event) -> None

Publish event.

**Parameters:**
- `event` (Event): Event object

##### clear() -> None

Clear all event handlers and filters.

##### set_max_recursion_depth(depth: int) -> None

Set maximum recursion depth.

**Parameters:**
- `depth` (int): Recursion depth

##### enable_async(enabled: bool) -> None

Enable or disable async event processing.

**Parameters:**
- `enabled` (bool): Whether to enable

##### get_handler_count(event_type: EventType) -> int

Get handler count for specified event type.

**Parameters:**
- `event_type` (EventType): Event type

**Returns:** Handler count

## Plugin Development

### Creating a Compute Plugin

```python
from gravitas.compute.vector_field import vector_calculator
from gravitas.core.events import Event, EventType, event_bus

class MyComputePlugin:
    def __init__(self):
        # Subscribe to relevant events
        event_bus.subscribe(EventType.GRID_UPDATED, self)

    def create_custom_pattern(self, grid):
        """Implement custom vector field pattern"""
        h, w = grid.shape[:2]
        for y in range(h):
            for x in range(w):
                # Create vortex pattern
                dx = x - w // 2
                dy = y - h // 2
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    vx = -dy / dist * 0.1
                    vy = dx / dist * 0.1
                    grid[y, x] = (vx, vy)
        return grid

    def handle(self, event: Event):
        """Handle event"""
        if event.type == EventType.GRID_UPDATED:
            grid = event.data.get('grid')
            if grid is not None:
                self.create_custom_pattern(grid)
```

### Creating a UI Plugin

```python
from plugins.ui import UIManager
from gravitas.input import input_handler, KeyMap
from gravitas.core.config import config_manager

class MyUIPlugin(UIManager):
    def register_callbacks(self, grid, **kwargs):
        super().register_callbacks(grid, **kwargs)

        def on_custom_key():
            # Toggle display mode
            current = config_manager.get("show_grid", True)
            config_manager.set("show_grid", not current)
            print(f"Grid display: {not current}")

        input_handler.register_key_callback(KeyMap.G, on_custom_key)

        def on_scale_up():
            current = config_manager.get("vector_scale", 1.0)
            config_manager.set("vector_scale", min(current + 0.1, 5.0))

        input_handler.register_key_callback(KeyMap.PLUS, on_scale_up)
```

### Event-Driven Development

```python
from gravitas.core.events import Event, EventType, event_bus, EventHandler

class MyEventHandler(EventHandler):
    def handle(self, event: Event):
        if event.type == EventType.VECTOR_UPDATED:
            print(f"Vector updated at {event.timestamp}")
        elif event.type == EventType.CONFIG_CHANGED:
            key = event.data.get('key')
            new_value = event.data.get('new_value')
            print(f"Config {key} changed to {new_value}")

# Register event handler
handler = MyEventHandler()
event_bus.subscribe(EventType.VECTOR_UPDATED, handler)
event_bus.subscribe(EventType.CONFIG_CHANGED, handler)
```

## Configuration Guide

Gravitas uses JSON configuration files with runtime hot updates and environment variable overrides.

### Complete Configuration Options

```json
{
  "grid_width": 640,
  "grid_height": 480,
  "cell_size": 1.0,
  "vector_color": [0.2, 0.6, 1.0],
  "vector_scale": 1.0,
  "vector_self_weight": 0.0,
  "vector_neighbor_weight": 0.25,
  "cam_x": 0.0,
  "cam_y": 0.0,
  "cam_zoom": 1.0,
  "show_grid": true,
  "grid_color": [0.3, 0.3, 0.3],
  "background_color": [0.1, 0.1, 0.1],
  "antialiasing": true,
  "line_width": 1.0,
  "compute_device": "cpu",
  "compute_iterations": 1,
  "render_vector_lines": true,
  "target_fps": 60
}
```

### Configuration Types and Validation

- **Number types**: Support range validation (min_value, max_value)
- **Boolean types**: true/false
- **Array types**: RGB colors, etc.
- **String types**: Device selection, etc., with option list support

### Environment Variable Support

```bash
export GRAVITAS_CONFIG=/path/to/config.json
```

### Runtime Configuration Updates

```python
from gravitas.core.config import config_manager

# Update configuration
config_manager.set("vector_scale", 2.0)
config_manager.set("compute_device", "gpu")

# Save to file
config_manager.save_config()
```

## Advanced Usage

### Batch Operation Optimization

```python
# Batch create vector influences
positions = [(100, 200, 1.0), (300, 150, 0.8), (500, 400, 1.2)]
vector_calculator.create_tiny_vectors_batch(grid, positions)

# Batch query vector values
query_positions = [(100, 200), (300, 150), (500, 400)]
vectors = vector_calculator.fit_vectors_at_positions_batch(grid, query_positions)
```

### State Management and Snapshots

```python
from gravitas.core.state import state_manager

# Create snapshot
snapshot = state_manager.create_snapshot()

# Modify state
state_manager.set("simulation_running", True)
state_manager.set("current_frame", 100)

# Restore snapshot
state_manager.restore_snapshot(snapshot)
```

### Custom Event Filtering

```python
from gravitas.core.events import EventTypeFilter, EventSourceFilter, CompositeFilter

# Only handle specific event types
type_filter = EventTypeFilter(EventType.VECTOR_UPDATED, EventType.GRID_UPDATED)

# Only handle events from specific sources
source_filter = EventSourceFilter("MyPlugin")

# Composite filter
composite_filter = CompositeFilter([type_filter, source_filter], logic="AND")

event_bus.subscribe(EventType.VECTOR_UPDATED, my_handler, composite_filter)
```

## License

MIT License
