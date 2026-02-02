# State management - unified state with change notifications and snapshots
import threading
import time
import copy
from typing import Any, Dict, Callable, Optional, List, Union
from dataclasses import dataclass, asdict
from .events import Event, EventType, event_bus

@dataclass
class StateChange:
    key: str
    old_value: Any
    new_value: Any
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class StateManager:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._listeners: Dict[str, List[Callable]] = {}
        self._change_history: List[StateChange] = []
        self._max_history_size = 100
        self._nested_level = 0

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any, notify: bool = True) -> None:
        with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value

            # record change history
            change = StateChange(key, old_value, value, time.time())
            self._change_history.append(change)

            # limit history size
            if len(self._change_history) > self._max_history_size:
                self._change_history.pop(0)

            # notify listeners if value changed
            if notify and old_value != value:
                self._notify_listeners(key, old_value, value)

    def update(self, updates: Dict[str, Any], notify: bool = True) -> None:
        with self._lock:
            for key, value in updates.items():
                self.set(key, value, notify=notify)

    def remove(self, key: str) -> bool:
        with self._lock:
            if key in self._state:
                old_value = self._state.pop(key)

                change = StateChange(key, old_value, None, time.time())
                self._change_history.append(change)

                if old_value is not None:
                    self._notify_listeners(key, old_value, None)

                return True
            return False

    def clear(self) -> None:
        with self._lock:
            old_state = copy.deepcopy(self._state)
            self._state.clear()

            change = StateChange("*", old_state, {}, time.time())
            self._change_history.append(change)

            for key in old_state:
                self._notify_listeners(key, old_state[key], None)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._state)

    def contains(self, key: str) -> bool:
        with self._lock:
            return key in self._state

    def add_listener(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        with self._lock:
            if key not in self._listeners:
                self._listeners[key] = []
            if callback not in self._listeners[key]:
                self._listeners[key].append(callback)

    def remove_listener(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        with self._lock:
            if key in self._listeners and callback in self._listeners[key]:
                self._listeners[key].remove(callback)

    def clear_listeners(self) -> None:
        with self._lock:
            self._listeners.clear()

    def _notify_listeners(self, key: str, old_value: Any, new_value: Any) -> None:
        if key in self._listeners:
            for callback in self._listeners[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    print(f"[StateManager] Error notifying listener: {e}")

    def get_change_history(self, key: Optional[str] = None, limit: Optional[int] = None) -> List[StateChange]:
        with self._lock:
            history = self._change_history

            # filter by key if specified
            if key is not None:
                history = [change for change in history if change.key == key]

            # limit records if specified
            if limit is not None and limit > 0:
                history = history[-limit:]

            return copy.deepcopy(history)

    def create_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "state": copy.deepcopy(self._state),
                "timestamp": time.time()
            }

    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        with self._lock:
            old_state = copy.deepcopy(self._state)
            self._state = copy.deepcopy(snapshot["state"])

            change = StateChange("*", old_state, self._state, time.time())
            self._change_history.append(change)

            # notify listeners for changed keys
            for key in old_state:
                if key in self._state:
                    if old_state[key] != self._state[key]:
                        self._notify_listeners(key, old_state[key], self._state[key])
                else:
                    self._notify_listeners(key, old_state[key], None)

            # notify for new keys
            for key in self._state:
                if key not in old_state:
                    self._notify_listeners(key, None, self._state[key])

    def __enter__(self):
        with self._lock:
            self._nested_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            self._nested_level -= 1

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.remove(key)

    def __contains__(self, key: str) -> bool:
        return self.contains(key)

    def __len__(self) -> int:
        with self._lock:
            return len(self._state)

    def __iter__(self):
        with self._lock:
            return iter(self._state.keys())

# global state manager instance
state_manager = StateManager()
