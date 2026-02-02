# Event system - pub/sub pattern with async support and filtering
import time
import asyncio
import threading
from enum import Enum
from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass

class EventType(Enum):
    # grid events
    GRID_UPDATED = "grid_updated"
    GRID_UPDATE_REQUEST = "grid_update_request"
    GRID_CLEARED = "grid_cleared"
    GRID_LOADED = "grid_loaded"
    GRID_SAVED = "grid_saved"
    TOGGLE_GRID = "toggle_grid"
    CLEAR_GRID = "clear_grid"

    # vector events
    VECTOR_UPDATED = "vector_updated"
    SET_MAGNITUDE = "set_magnitude"
    TOGGLE_REVERSE_VECTOR = "toggle_reverse_vector"

    # view events
    VIEW_CHANGED = "view_changed"
    VIEW_RESET = "view_reset"
    RESET_VIEW = "reset_view"

    # toolbar events
    SET_BRUSH_SIZE = "set_brush_size"

    # app events
    APP_INITIALIZED = "app_initialized"
    APP_SHUTDOWN = "app_shutdown"

    # config events
    CONFIG_CHANGED = "config_changed"

    # async events
    ASYNC_EVENT_PROCESSED = "async_event_processed"

    # gpu compute events
    GPU_COMPUTE_STARTED = "gpu_compute_started"
    GPU_COMPUTE_COMPLETED = "gpu_compute_completed"
    GPU_COMPUTE_ERROR = "gpu_compute_error"

    # mouse events
    MOUSE_CLICKED = "mouse_clicked"
    MOUSE_MOVED = "mouse_moved"
    MOUSE_SCROLLED = "mouse_scrolled"

    # keyboard events
    KEY_PRESSED = "key_pressed"
    KEY_RELEASED = "key_released"

@dataclass
class Event:
    type: EventType
    data: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def __str__(self):
        return f"Event(type={self.type}, source={self.source}, timestamp={self.timestamp})"

class EventHandler:
    def handle(self, event: Event) -> None:
        pass

    def can_handle(self, event: Event) -> bool:
        return True

class AsyncEventHandler(EventHandler):
    async def handle_async(self, event: Event) -> None:
        pass

    def handle(self, event: Event) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.handle_async(event))
        except RuntimeError:
            asyncio.run(self.handle_async(event))

class EventFilter:
    def filter(self, event: Event) -> bool:
        return True

class EventTypeFilter(EventFilter):
    def __init__(self, *allowed_types: EventType):
        self.allowed_types = allowed_types

    def filter(self, event: Event) -> bool:
        return event.type in self.allowed_types

class EventSourceFilter(EventFilter):
    def __init__(self, *allowed_sources: str):
        self.allowed_sources = allowed_sources

    def filter(self, event: Event) -> bool:
        return event.source in self.allowed_sources

class CompositeFilter(EventFilter):
    def __init__(self, filters: List[EventFilter], logic: str = "AND"):
        self.filters = filters
        self.logic = logic.upper()

    def filter(self, event: Event) -> bool:
        if not self.filters:
            return True

        if self.logic == "AND":
            return all(f.filter(event) for f in self.filters)
        elif self.logic == "OR":
            return any(f.filter(event) for f in self.filters)
        else:
            raise ValueError(f"Unsupported logic operation: {self.logic}")

class FunctionEventHandler(EventHandler):
    def __init__(self, func: Callable[[Event], None], name: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__

    def handle(self, event: Event) -> None:
        self.func(event)

    def __str__(self):
        return f"FunctionEventHandler({self.name})"

class AsyncFunctionEventHandler(AsyncEventHandler):
    def __init__(self, func: Callable[[Event], Any], name: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__

    async def handle_async(self, event: Event) -> None:
        await self.func(event)

    def __str__(self):
        return f"AsyncFunctionEventHandler({self.name})"

class EventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._filters: Dict[EventType, List[EventFilter]] = {}
        self._lock = threading.Lock()
        self._recursion_depth = 0
        self._max_recursion_depth = 10
        self._async_enabled = True

    def subscribe(self, event_type: EventType, handler: EventHandler,
                 filter: Optional[EventFilter] = None) -> None:
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []

            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)

                # save filter if provided
                if filter is not None:
                    if event_type not in self._filters:
                        self._filters[event_type] = []
                    self._filters[event_type].append(filter)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        with self._lock:
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

                # remove filters if no handlers left
                if event_type in self._filters and not self._handlers[event_type]:
                    self._filters.pop(event_type, None)

    def publish(self, event: Event) -> None:
        # check recursion depth
        if self._recursion_depth >= self._max_recursion_depth:
            print(f"[EventBus] Warning: Recursion depth exceeded ({self._max_recursion_depth}), stopping event: {event.type}")
            return

        with self._lock:
            handlers = self._handlers.get(event.type, []).copy()
            filters = self._filters.get(event.type, []).copy()

        # apply filters
        if filters:
            for filter in filters:
                if not filter.filter(event):
                    return

        self._recursion_depth += 1

        try:
            # handle events synchronously
            for handler in handlers:
                try:
                    handler.handle(event)
                except Exception as e:
                    print(f"[EventBus] Error handling event: {e}")
                    self._publish_error_event(event, e)

            # publish async processed event if enabled
            if self._async_enabled and event.type not in [EventType.ASYNC_EVENT_PROCESSED, EventType.APP_INITIALIZED]:
                async_event = Event(EventType.ASYNC_EVENT_PROCESSED, {
                    "original_event": str(event),
                    "async_enabled": True
                }, "EventBus")
                self.publish(async_event)
        finally:
            self._recursion_depth -= 1

    async def publish_async(self, event: Event) -> None:
        if self._recursion_depth > self._max_recursion_depth:
            print(f"[EventBus] Warning: Recursion depth exceeded ({self._max_recursion_depth}), stopping event: {event.type}")
            return

        with self._lock:
            handlers = self._handlers.get(event.type, []).copy()
            filters = self._filters.get(event.type, []).copy()

        if filters:
            for filter in filters:
                if not filter.filter(event):
                    return

        self._recursion_depth += 1

        try:
            async_tasks = []
            for handler in handlers:
                try:
                    if isinstance(handler, AsyncEventHandler):
                        async_tasks.append(handler.handle_async(event))
                    else:
                        handler.handle(event)
                except Exception as e:
                    print(f"[EventBus] Error handling event: {e}")
                    await self._publish_error_event_async(event, e)

            if async_tasks:
                await asyncio.gather(*async_tasks, return_exceptions=True)
        finally:
            self._recursion_depth -= 1

    def _publish_error_event(self, original_event: Event, error: Exception) -> None:
        try:
            error_event = Event(
                EventType.GPU_COMPUTE_ERROR,
                {"original_event": str(original_event), "error": str(error)},
                "EventBus"
            )
            self.publish(error_event)
        except Exception:
            pass

    async def _publish_error_event_async(self, original_event: Event, error: Exception) -> None:
        try:
            error_event = Event(
                EventType.GPU_COMPUTE_ERROR,
                {"original_event": str(original_event), "error": str(error)},
                "EventBus"
            )
            await self.publish_async(error_event)
        except Exception:
            pass

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()
            self._filters.clear()

    def set_max_recursion_depth(self, depth: int) -> None:
        self._max_recursion_depth = depth

    def enable_async(self, enabled: bool) -> None:
        self._async_enabled = enabled

    def get_handler_count(self, event_type: EventType) -> int:
        with self._lock:
            return len(self._handlers.get(event_type, []))

# global event bus instance
event_bus = EventBus()
