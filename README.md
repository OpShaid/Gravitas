
# Gravitas

![Licence](https://img.shields.io/badge/Licence-MIT-96d35f?style=flat)
![Version](https://img.shields.io/badge/Version-0.1.0Alpha-000000?style=flat)
![Language](https://img.shields.io/badge/Language-Python-f5ec00?style=flat)

## Table of Contents

- [Project Overview](#project-overview)
- [Video Demo](#video-demo)
- [Installation and Running](#installation-and-running)
  - [System Requirements](#system-requirements)
  - [Download](#download)
  - [Install Dependencies](#install-dependencies)
  - [Run Examples](#run-examples)
  - [Keyboard Controls](#keyboard-controls)
- [Vector Field Computation Principles](#vector-field-computation-principles)
  - [Basic Concepts](#basic-concepts)
  - [Computation Methods](#computation-methods)
  - [Supported Vector Field Modes](#supported-vector-field-modes)
  - [CPU vs GPU Computation](#cpu-vs-gpu-computation)
- [Architecture Design](#architecture-design)
  - [Core Engine (gravitas/)](#core-engine-gravitas)
  - [Plugin System (plugins/)](#plugin-system-plugins)
- [Configuration Guide](#configuration-guide)
- [Changelog](#changelog)
- [FAQ](#faq)
- [License](#license)
- [Contact](#contact)
- [Contributing](#contributing)

## Project Overview

Gravitas is a vector field-driven physics engine that simulates physical force fields (such as electromagnetic forces) to drive entity motion. This fundamentally solves the performance bottleneck of traditional collision detection methods. Instead of iterating through every entity pair for calculations, entities only need to independently compute the vector value at their coordinates to handle force interactions.

## Video Demo



[A Physics Engine Without Collision Detection - YouTube](https://youtube.com/shorts/vhOnfVl3CO8?si=xlLsO2X8CiU1n6YD)

## Installation and Running

### System Requirements

- Python 3.7+
- OpenGL support
- OpenCL runtime for GPU computation (optional)

### Download

Download and extract the source code directly. The release version contains the packaged core library.

### Install Dependencies

```bash
pip install -r requirements.txt
# Or use pip install gravitas to install the core library directly
```

Main dependencies:
- numpy>=1.21.0 (numerical computation)
- glfw>=2.5.0 (window management)
- PyOpenGL>=3.1.6 (OpenGL rendering)
- pyopencl>=2021.1.0 (GPU computation, optional)
- pybind11>=2.6.0 (C++ bindings)

### Run Examples

```bash
# Basic usage example - demonstrates core functionality
python examples/basic_usage.py

# Gravity box example - physics simulation
python examples/gravity_box.py

# Input demo - interactive features showcase
python examples/input_demo.py
```

### Keyboard Controls

- **Spacebar**: Regenerate tangent mode
- **G key**: Toggle grid display
- **C key**: Clear grid
- **U key**: Toggle real-time update
- **Mouse drag**: Pan view
- **Scroll wheel**: Zoom view

## Vector Field Computation Principles

### Basic Concepts

A vector field is a two-dimensional grid data structure where each grid point contains a two-dimensional vector `(vx, vy)` representing the direction and magnitude at that point. Vector field computation involves mutual influence between adjacent points, forming complex dynamic patterns.

### Computation Methods

#### 1. Adjacent Vector Summation
For each grid point, compute the weighted sum of itself and its four neighbors (up, down, left, right):

```python
new_vector = self_value * self_weight + neighbor_sum * neighbor_weight
```

- **Self weight** (`vector_self_weight`): Controls the influence of the point's own vector on the result
- **Neighbor weight** (`vector_neighbor_weight`): Controls the influence of neighbor vectors on the result

#### 2. Vector Field Update
Iterate and update each vector value in the field:

```python
# Vector field update
vector_calculator.update_grid_with_adjacent_sum(grid)
```

#### 3. Bilinear Interpolation
When adding or reading vectors at floating-point coordinates, bilinear interpolation is used for smooth processing:

```python
# Fit a vector at specified position
fit_vector_at_position(grid, x, y)

# Add a vector at specified position
add_vector_at_position(grid, x, y, vx, vy)
```

### Supported Vector Field Modes

#### Tiny Vector Addition
Create local influence at a specified position, affecting only the current position and its four neighbors:

```python
create_tiny_vector(self, grid, x, y, mag)
```

### CPU vs GPU Computation

- **CPU Computation**: Uses NumPy vectorized operations, suitable for small to medium scale computation, easy to debug
- **GPU Computation**: Uses OpenCL acceleration for large-scale parallel computation, significantly improved performance, suitable for real-time applications

## Architecture Design

### Core Engine (gravitas/)

- **core**: Core module
- **compute**: Computation module with unified interface for CPU and GPU computation
- **graphics**: Renderer module
- **window**: Window manager module
- **input**: Input manager module

### Plugin System (plugins/)

- **controller.py**: Controller plugin for handling user input and vector field operations
- **marker_system.py**: Marker system supporting marker points on the vector field
- **ui.py**: UI manager for handling interface interaction and event dispatch

## Configuration Guide

Main configuration options in `config.json`:

```json
{
    "grid": {
        "width": 640,
        "height": 480,
        "color": [0.3, 0.3, 0.3]
    },
    "cell": {
        "size": 2.0  // Cell size
    },
    "vector": {
        "color": [0.2, 0.6, 1.0],
        "scale": 1.0,  // Vector length scale
        "self": {
            "weight": 0.2  // Self weight
        },
        "neighbor": {
            "weight": 0.2  // Neighbor weight
        }
    },
    "cam": {
        "x": 0.0,
        "y": 0.0,
        "zoom": 1.0
    },
    "show": {
        "grid": true  // Whether to show grid lines
    },
    "background": {
        "color": [0.1, 0.1, 0.1]
    },
    "antialiasing": true,  // Enable antialiasing
    "line": {
        "width": 1.0  // Line width
    },
    "compute": {
        "device": "gpu",  // Compute device: cpu or gpu
        "iterations": 1  // Iteration count
    },
    "render": {
        "vector": {
            "lines": false  // Whether to show vector lines
        }
    }
}
```

## Changelog

### v0.1.0 Alpha (2026-01-01)
- Initial release
- Support for vector field-driven physics simulation
- Implemented CPU and GPU computation modes
- Provided basic plugin system
- Included multiple example programs

## FAQ

### Q: How do I switch between CPU and GPU computation modes?
A: Set `"compute": {"device": "cpu"}` or `"gpu"` in `config.json`.

### Q: What if I get OpenGL errors when running examples?
A: Ensure your system supports OpenGL and has appropriate graphics drivers installed.

### Q: How do I add custom vector field modes?
A: Refer to existing modes in `gravitas/compute/vector_field.py` and implement new computation functions.

### Q: Which operating systems are supported?
A: Currently primarily tested on Windows. Other operating systems may require dependency adjustments.

## License

[MIT License](LICENSE)

## Contact

shaidt137@gmail.com

## Contributing

This project is in the demo stage and may have some undiscovered issues.
We need your support and assistance!
If you're interested, please give us a star to help us reach more people!

### How to Contribute

1. **Report Issues**: If you find bugs or have feature suggestions, please submit them in GitHub Issues.
2. **Submit Code**: Fork this repository, create a feature branch, and submit a PR.
3. **Improve Documentation**: Help improve documentation or add examples.
4. **Testing**: Test on different platforms and report compatibility issues.

### Development Environment Setup

```bash
git clone https://github.com/OpShaid/Gravitas.git
cd Gravitas
pip install -r requirements.txt
```

### Code Standards

- Use PEP 8 style
- Add necessary comments and docstrings
- Test before submitting

### API Documentation

For detailed API documentation, see the files in the `doc/` directory:
- [README.md](doc/README.md)
