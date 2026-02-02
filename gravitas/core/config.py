# Config management module - file loading and hot updates
import json
import logging
import os
import sys
import threading
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, asdict, field
from .state import StateManager, state_manager
from .events import Event, EventBus, EventType, event_bus

@dataclass
class ConfigOption:
    key: str
    value: Any
    default: Any
    description: str = ""
    type: str = "string"  # string, number, boolean, array, object
    options: List[Any] = field(default_factory=list)
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigOption':
        return cls(**data)

class ConfigManager:
    def __init__(self, config_file: Optional[str] = None):
        self._config_file = config_file
        self._options: Dict[str, ConfigOption] = {}
        self._lock = threading.RLock()
        self._state_manager = state_manager
        self._event_bus = event_bus
        self._logger = logging.getLogger(__name__)

        # init default config
        self._init_default_config()

        # load config file if specified
        if self._config_file and os.path.exists(self._config_file):
            self.load_from_file(self._config_file)

    def _init_default_config(self) -> None:
        # grid config
        self.register_option("grid_width", 640, "Grid width", type="number")
        self.register_option("grid_height", 480, "Grid height", type="number")
        self.register_option("cell_size", 1.0, "Cell size", type="number")

        # vector field config
        self.register_option("vector_color", [0.2, 0.6, 1.0], "Vector color", type="array")
        self.register_option("vector_scale", 1.0, "Vector scale", type="number", min_value=0.1, max_value=10.0)
        self.register_option("vector_self_weight", 0.0, "Vector self weight", type="number", min_value=0.0, max_value=10.0)
        self.register_option("vector_neighbor_weight", 0.25, "Vector neighbor weight", type="number", min_value=0.0, max_value=10.0)

        # view config
        self.register_option("cam_x", 0.0, "Camera X", type="number")
        self.register_option("cam_y", 0.0, "Camera Y", type="number")
        self.register_option("cam_zoom", 1.0, "Camera zoom", type="number", min_value=0.1, max_value=10.0)
        self.register_option("show_grid", True, "Show grid", type="boolean")
        self.register_option("grid_color", [0.3, 0.3, 0.3], "Grid color", type="array")

        # render config
        self.register_option("background_color", [0.1, 0.1, 0.1], "Background color", type="array")
        self.register_option("antialiasing", True, "Enable antialiasing", type="boolean")
        self.register_option("line_width", 1.0, "Line width", type="number", min_value=0.5, max_value=5.0)

        # compute config
        self.register_option("compute_device", "cpu", "Compute device", options=["cpu", "gpu"])
        self.register_option("compute_iterations", 1, "Compute iterations", type="number", min_value=1, max_value=100)

        # render vector lines
        self.register_option("render_vector_lines", True, "Render vector lines", type="boolean")

        # fps config
        self.register_option("target_fps", 60, "Target FPS", type="number", min_value=1, max_value=240)

    def register_option(self, key: str, default: Any, description: str = "",
                       type: str = "string", options: List[Any] = None,
                       min_value: Optional[Union[int, float]] = None,
                       max_value: Optional[Union[int, float]] = None) -> None:
        with self._lock:
            if key in self._options:
                # update existing option metadata
                option = self._options[key]
                option.description = description
                option.type = type
                if options is not None:
                    option.options = options
                option.min_value = min_value
                option.max_value = max_value
            else:
                # create new option
                option = ConfigOption(
                    key=key,
                    value=default,
                    default=default,
                    description=description,
                    type=type,
                    options=options or [],
                    min_value=min_value,
                    max_value=max_value
                )
                self._options[key] = option

            # set default if not in state manager
            if not self._state_manager.contains(key):
                self._state_manager.set(key, default, notify=False)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            flat_key = key.replace('.', '_')
            if flat_key in self._options:
                return self._state_manager.get(flat_key, self._options[flat_key].value)
            return self._state_manager.get(flat_key, default)

    def set(self, key: str, value: Any) -> bool:
        with self._lock:
            flat_key = key.replace('.', '_')
            if flat_key not in self._options:
                # dynamicly register unknown option
                self.register_option(flat_key, value, f"Dynamic option: {key}")

            option = self._options[flat_key]

            # type check
            if not self._validate_value(value, option):
                self._logger.warning(f"Config value type or range mismatch: {key} = {value}")
                return False

            old_value = self._state_manager.get(flat_key, option.value)
            self._state_manager.set(flat_key, value)

            # publish change event if value changed
            if old_value != value:
                self._event_bus.publish(Event(
                    EventType.CONFIG_CHANGED,
                    {"key": key, "old_value": old_value, "new_value": value},
                    "ConfigManager"
                ))

            # save config if file is set
            if self._config_file:
                self.save_to_file(self._config_file)

            return True

    def _validate_value(self, value: Any, option: ConfigOption) -> bool:
        if option.type == "boolean":
            return isinstance(value, bool)
        elif option.type == "number":
            if not isinstance(value, (int, float)):
                return False
            if option.min_value is not None and value < option.min_value:
                return False
            if option.max_value is not None and value > option.max_value:
                return False
            return True
        elif option.type == "array":
            return isinstance(value, list)
        elif option.type == "object":
            return isinstance(value, dict)
        else:  # string
            return isinstance(value, str)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            config = {}
            for key, option in self._options.items():
                config[key] = self._state_manager.get(key, option.value)
            return config

    def _nest_dict_from_flat(self, flat: Dict[str, Any]) -> Dict[str, Any]:
        nested: Dict[str, Any] = {}
        for flat_key, value in flat.items():
            if not flat_key:
                continue
            parts = flat_key.split('_')
            cur = nested
            for i, part in enumerate(parts):
                if not part:
                    continue
                if i == len(parts) - 1:
                    cur[part] = value
                else:
                    if part not in cur or not isinstance(cur[part], dict):
                        cur[part] = {}
                    cur = cur[part]
        return nested

    def _flatten_dict(self, nested: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        items: Dict[str, Any] = {}
        for k, v in nested.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key))
            else:
                items[new_key] = v
        return items

    def reset_to_default(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key is None:
                # reset all
                for option in self._options.values():
                    self._state_manager.set(option.key, option.default)

                self._event_bus.publish(Event(
                    EventType.CONFIG_CHANGED,
                    {"action": "reset_all"},
                    "ConfigManager"
                ))
            else:
                # reset single
                flat_key = key.replace('.', '_')
                if flat_key in self._options:
                    option = self._options[flat_key]
                    self._state_manager.set(flat_key, option.default)

                    self._event_bus.publish(Event(
                        EventType.CONFIG_CHANGED,
                        {"key": key, "action": "reset"},
                        "ConfigManager"
                    ))

    def load_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            flat_config: Dict[str, Any] = {}
            if isinstance(config_data, dict):
                flat_config = self._flatten_dict(config_data)

            with self._lock:
                for key, value in flat_config.items():
                    if key in self._options:
                        self.set(key, value)
                    else:
                        if key in self._options:
                            self.set(key, value)

            return True
        except Exception as e:
            self._logger.error(f"Failed to load config: {file_path}, error: {e}")
            return False

    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        try:
            config_file = file_path or self._config_file
            if not config_file:
                return False

            all_config = self._state_manager.get_all()

            dir_name = os.path.dirname(config_file)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(all_config, f, indent=4)

            return True
        except Exception as e:
            self._logger.error(f"Failed to save config: {config_file}, error: {e}")
            return False

    def load_config(self) -> bool:
        return self.load_from_file(self._config_file) if self._config_file else False

    def save_config(self) -> bool:
        return self.save_to_file(self._config_file) if self._config_file else False

    def get_option_info(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if key in self._options:
                return self._options[key].to_dict()
            return None

    def get_all_option_info(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {key: option.to_dict() for key, option in self._options.items()}

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self._options

# global config manager
# config path lookup: env var -> cwd -> exe dir
env_path = os.environ.get("GRAVITAS_CONFIG")
if env_path:
    config_path = env_path
else:
    cwd_path = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(cwd_path):
        config_path = cwd_path
    else:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_dir, "config.json")

config_manager = ConfigManager(config_path)
