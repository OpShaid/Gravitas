# Gravitas - Engine Architecture Documentation

## Executive Summary

Gravitas is a vector field-driven physics engine built from scratch in Python. Unlike traditional collision detection approaches that require O(n²) pairwise entity comparisons, Gravitas uses continuous vector fields to compute forces, achieving O(n) complexity for entity physics calculations.

The engine was designed to demonstrate proficiency in:
- **Scene Graph / Entity Management** - MarkerSystem manages entities with position, velocity, and magnitude properties
- **Canvas Interaction Mathematics** - Bilinear interpolation, coordinate transforms, viewport management
- **Application Logic Architecture** - Event-driven design, dependency injection, state management

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│                                        
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                        Core Engine                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     AppCore                               │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────────────┐    │   │
│  │  │GridManager │ │ViewManager │ │  FPSLimiter        │    │   │
│  │  └────────────┘ └────────────┘ └────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  EventBus    │  │ StateManager │  │   ConfigManager      │   │
│  │ (pub/sub)    │  │ (snapshots)  │  │   (hot reload)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Dependency Injection Container               │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      Compute Layer                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                VectorFieldCalculator                      │   │
│  │        (unified interface for CPU/GPU switching)          │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐    │   │
│  │  │ CPUVectorCalculator │  │  GPUVectorCalculator    │    │   │
│  │  │     (NumPy)         │  │      (OpenCL)           │    │   │
│  │  └─────────────────────┘  └─────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Graphics / Window Layer                       │
│  ┌───────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ VectorFieldRenderer│  │    Window      │  │  InputHandler  │  │
│  │    (OpenGL 3.3+)   │  │    (GLFW)      │  │  (callbacks)   │  │
│  └───────────────────┘  └────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Scene Graph Implementation: MarkerSystem

The `MarkerSystem` class (`plugins/marker_system.py`) implements entity management similar to a scene graph:

### Data Structure
```python
marker = {
    'x': float,      # grid X position
    'y': float,      # grid Y position
    'mag': float,    # magnitude/mass for vector influence
    'vx': float,     # velocity X component
    'vy': float      # velocity Y component
}
```

### Key Operations

**1. Entity Creation**
```python
def add_marker(self, x: float, y: float, mag: float = 1.0,
               vx: float = 0.0, vy: float = 0.0):
    marker = {'x': x, 'y': y, 'mag': mag, 'vx': vx, 'vy': vy}
    self._markers.append(marker)
    self._sync_to_state_manager()
```

**2. Physics Update Loop**
```python
def update_markers(self, grid, cell_size, gravity, speed_factor):
 
    positions = [(m['x'], m['y']) for m in self._markers]
    vectors = vector_calculator.fit_vectors_at_positions_batch(grid, positions)

    for i, marker in enumerate(self._markers):
        vx, vy = vectors[i]

    
        marker['vx'] += vx * marker['mag']
        marker['vy'] += vy * marker['mag']

 
        speed = math.sqrt(marker['vx']**2 + marker['vy']**2)
        if speed > cell_size:
            marker['vx'] = (marker['vx'] / speed) * cell_size
            marker['vy'] = (marker['vy'] / speed) * cell_size

        marker['x'] += marker['vx']
        marker['y'] += marker['vy']

    
        marker['vy'] += gravity
        marker['vx'] *= speed_factor
        marker['vy'] *= speed_factor
```

**3. Batch Vector Field Influence**
```python
def apply_marker_influences(self, grid):
   
    positions = [(m['x'], m['y'], m['mag']) for m in self._markers]

    
    vector_calculator.create_tiny_vectors_batch(grid, positions)
```

---

## Canvas Interaction Mathematics

### Coordinate System Transforms

The engine uses three coordinate spaces:
1. **Screen Space** - pixel coordinates from input events
2. **World Space** - continuous coordinates with camera offset/zoom
3. **Grid Space** - discrete cell coordinates for vector field

```python
def screen_to_grid(self, screen_x, screen_y, window_width, window_height):
 
    cam_x = state_manager.get("cam_x", 0.0)
    cam_y = state_manager.get("cam_y", 0.0)
    cam_zoom = state_manager.get("cam_zoom", 1.0)
    cell_size = config_manager.get("cell_size", 1.0)

 
    world_x = (screen_x - window_width / 2) / cam_zoom + cam_x
    world_y = (window_height / 2 - screen_y) / cam_zoom + cam_y

  
    grid_x = world_x / cell_size
    grid_y = world_y / cell_size

    return grid_x, grid_y
```

### Bilinear Interpolation

For smooth vector field sampling at floating-point coordinates:

```python
def fit_vector_at_position(self, grid, x, y):
  
    x0, y0 = int(x), int(y)
    x1, y1 = x0 + 1, y0 + 1


    h, w = grid.shape[:2]
    x0, x1 = max(0, min(x0, w-1)), max(0, min(x1, w-1))
    y0, y1 = max(0, min(y0, h-1)), max(0, min(y1, h-1))

   
    fx, fy = x - int(x), y - int(y)

   
    v00 = grid[y0, x0]  # top-left
    v01 = grid[y0, x1]  # top-right
    v10 = grid[y1, x0]  # bottom-left
    v11 = grid[y1, x1]  # bottom-right

    vx = (v00[0] * (1-fx) * (1-fy) + v01[0] * fx * (1-fy) +
          v10[0] * (1-fx) * fy + v11[0] * fx * fy)
    vy = (v00[1] * (1-fx) * (1-fy) + v01[1] * fx * (1-fy) +
          v10[1] * (1-fx) * fy + v11[1] * fx * fy)

    return vx, vy
```

### View/Camera Management

```python
class ViewManager:
    def handle_scroll_zoom(self, scroll_delta, mouse_x, mouse_y):
    
        old_zoom = state_manager.get("cam_zoom")
        new_zoom = max(0.1, min(10.0, old_zoom * (1.1 ** scroll_delta)))

  
        cam_x = state_manager.get("cam_x")
        cam_y = state_manager.get("cam_y")

        zoom_ratio = new_zoom / old_zoom
        cam_x = mouse_x - (mouse_x - cam_x) * zoom_ratio
        cam_y = mouse_y - (mouse_y - cam_y) * zoom_ratio

        state_manager.update({
            "cam_x": cam_x,
            "cam_y": cam_y,
            "cam_zoom": new_zoom
        })
```

---

## Class Structure & Design Patterns

### 1. Dependency Injection Container

Thread-safe IoC container with automatic constructor injection:

```python
class Container:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._lock = threading.RLock()

    def register_singleton(self, service_type: Type[T], instance: T):
        with self._lock:
            descriptor = ServiceDescriptor(lambda: instance, singleton=True)
            descriptor.instance = instance
            self._services[service_type] = descriptor

    def resolve(self, service_type: Type[T]) -> Optional[T]:
        with self._lock:
            if service_type not in self._services:
                return None
            return self._services[service_type].get_instance(self)
```

**Auto-injection example:**
```python
class MyService:
    def __init__(self, config: ConfigManager, events: EventBus):
        # Dependencies automatically resolved from container
        self.config = config
        self.events = events

# Registration
container.register(MyService, MyService)

# Resolution with auto-injection
service = container.resolve(MyService)  # ConfigManager and EventBus injected
```

### 2. Event-Driven Architecture (Pub/Sub)

```python
class EventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._filters: Dict[EventType, List[EventFilter]] = {}
        self._lock = threading.Lock()
        self._max_recursion_depth = 10

    def subscribe(self, event_type: EventType, handler: EventHandler,
                  filter: Optional[EventFilter] = None):
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)

    def publish(self, event: Event):
        # Recursion protection
        if self._recursion_depth >= self._max_recursion_depth:
            return

        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            handler.handle(event)
```

**Event Types:**
- Grid events: `GRID_UPDATED`, `GRID_CLEARED`, `GRID_LOADED`
- View events: `VIEW_CHANGED`, `VIEW_RESET`
- Input events: `MOUSE_CLICKED`, `KEY_PRESSED`
- Config events: `CONFIG_CHANGED`
- GPU events: `GPU_COMPUTE_STARTED`, `GPU_COMPUTE_COMPLETED`

### 3. State Management with Snapshots

```python
class StateManager:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._listeners: Dict[str, List[Callable]] = {}
        self._history: List[StateChange] = []

    def set(self, key: str, value: Any, notify: bool = True):
        old_value = self._state.get(key)
        self._state[key] = value

        # Track change history
        self._history.append(StateChange(key, old_value, value))

        # Notify listeners
        if notify and key in self._listeners:
            for callback in self._listeners[key]:
                callback(key, old_value, value)

    def create_snapshot(self) -> Dict[str, Any]:
        return copy.deepcopy(self._state)

    def restore_snapshot(self, snapshot: Dict[str, Any]):
        self._state = copy.deepcopy(snapshot)
```

---

## GPU Compute Pipeline (OpenCL)

### Architecture

```python
class GPUVectorFieldCalculator:
    def __init__(self):
        # Initialize OpenCL context
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)

        # Compile kernels
        self.program = cl.Program(self.ctx, KERNEL_SOURCE).build()

    def update_grid_with_adjacent_sum(self, grid):
        # Upload grid to GPU
        grid_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE |
                             cl.mem_flags.COPY_HOST_PTR, hostbuf=grid)

        # Execute kernel
        self.program.adjacent_sum(
            self.queue, grid.shape[:2], None,
            grid_buf, np.int32(grid.shape[1]), np.int32(grid.shape[0]),
            np.float32(self_weight), np.float32(neighbor_weight)
        )

        # Download result
        cl.enqueue_copy(self.queue, grid, grid_buf)
        return grid
```

### OpenCL Kernel

```c
__kernel void adjacent_sum(
    __global float2* grid,
    int width, int height,
    float self_weight, float neighbor_weight
) {
    int x = get_global_id(0);
    int y = get_global_id(1);

    if (x >= width || y >= height) return;

    float2 self_vec = grid[y * width + x];
    float2 sum = (float2)(0.0f, 0.0f);

    // Sum adjacent vectors
    if (x > 0) sum += grid[y * width + (x-1)];
    if (x < width-1) sum += grid[y * width + (x+1)];
    if (y > 0) sum += grid[(y-1) * width + x];
    if (y < height-1) sum += grid[(y+1) * width + x];

    // Apply weights
    grid[y * width + x] = self_vec * self_weight + sum * neighbor_weight;
}
```

---

## Plugin System

Dynamic plugin loading with importlib:

```python
class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugins = {}
        self._load_plugins(plugin_dir)

    def _load_plugins(self, plugin_dir):
        for file in os.listdir(plugin_dir):
            if file.endswith('.py') and not file.startswith('_'):
                module_name = file[:-3]
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    os.path.join(plugin_dir, file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins[module_name] = module
```

**Available Plugins:**
- `controller.py` - Business logic for user interactions
- `marker_system.py` - Entity/marker management
- `ui.py` - Input callbacks and UI event handling
- `command.py` - Terminal-style command interpreter
- `toolkit.py` - Utility functions for vector field manipulation

---

## Performance Considerations

1. **Batch Operations** - Vector operations are batched to minimize Python overhead
2. **NumPy Vectorization** - CPU calculations use vectorized NumPy operations
3. **GPU Acceleration** - OpenCL kernels for large-scale parallel computation
4. **Object Pooling** - Markers reuse allocated memory when possible
5. **Spatial Optimization** - Vector field allows O(n) force lookups vs O(n²) collision

---

## Testing

The engine includes comprehensive tests:
- `test_vector_field.py` - Vector calculation accuracy
- `test_events.py` - Event pub/sub functionality
- `test_state.py` - State management and snapshots
- `test_container.py` - Dependency injection
- `test_marker_performance.py` - Benchmarks with 100-10000 markers

---

## License

MIT License - Copyright (c) 2025 OpShaid
