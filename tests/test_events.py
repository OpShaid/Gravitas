import pytest
import asyncio
from unittest.mock import Mock, MagicMock
from gravitas.core.events import (
    Event, EventType, EventHandler, AsyncEventHandler,
    EventFilter, EventTypeFilter, EventSourceFilter, CompositeFilter,
    FunctionEventHandler, AsyncFunctionEventHandler, EventBus, event_bus
)


class TestEvent:
    

    def test_event_creation(self):
        
        event = Event(EventType.APP_INITIALIZED, {"key": "value"}, "test_source")

        assert event.type == EventType.APP_INITIALIZED
        assert event.data == {"key": "value"}
        assert event.source == "test_source"
        assert isinstance(event.timestamp, float)

    def test_event_str_representation(self):
        
        event = Event(EventType.APP_INITIALIZED)
        str_repr = str(event)

        assert "Event(type=EventType.APP_INITIALIZED" in str_repr
        assert "timestamp=" in str_repr


class TestEventHandler:
    

    def test_event_handler_handle(self):
        
        handler = EventHandler()
        event = Event(EventType.APP_INITIALIZED)

        handler.handle(event)

    def test_event_handler_can_handle(self):
        
        handler = EventHandler()
        event = Event(EventType.APP_INITIALIZED)

        assert handler.can_handle(event)


class TestAsyncEventHandler:
    

    def test_async_event_handler_handle(self):
        
        handler = AsyncEventHandler()
        event = Event(EventType.APP_INITIALIZED)

        handler.handle(event)

    @pytest.mark.asyncio
    async def test_async_event_handler_handle_async(self):
        
        handler = AsyncEventHandler()
        event = Event(EventType.APP_INITIALIZED)

        await handler.handle_async(event)


class TestEventFilters:
    

    def test_event_type_filter(self):
        
        filter = EventTypeFilter(EventType.APP_INITIALIZED, EventType.APP_SHUTDOWN)

        event1 = Event(EventType.APP_INITIALIZED)
        event2 = Event(EventType.GRID_UPDATED)

        assert filter.filter(event1)
        assert not filter.filter(event2)

    def test_event_source_filter(self):
        
        filter = EventSourceFilter("source1", "source2")

        event1 = Event(EventType.APP_INITIALIZED, source="source1")
        event2 = Event(EventType.APP_INITIALIZED, source="source3")

        assert filter.filter(event1)
        assert not filter.filter(event2)

    def test_composite_filter_and(self):
        
        type_filter = EventTypeFilter(EventType.APP_INITIALIZED)
        source_filter = EventSourceFilter("test")
        composite = CompositeFilter([type_filter, source_filter], "AND")

        event1 = Event(EventType.APP_INITIALIZED, source="test")
        event2 = Event(EventType.APP_INITIALIZED, source="other")
        event3 = Event(EventType.GRID_UPDATED, source="test")

        assert composite.filter(event1)
        assert not composite.filter(event2)
        assert not composite.filter(event3)

    def test_composite_filter_or(self):
        
        type_filter = EventTypeFilter(EventType.APP_INITIALIZED)
        source_filter = EventSourceFilter("test")
        composite = CompositeFilter([type_filter, source_filter], "OR")

        event1 = Event(EventType.APP_INITIALIZED, source="other")
        event2 = Event(EventType.GRID_UPDATED, source="test")
        event3 = Event(EventType.GRID_UPDATED, source="other")

        assert composite.filter(event1)
        assert composite.filter(event2)
        assert not composite.filter(event3)


class TestFunctionEventHandlers:
    

    def test_function_event_handler(self):
        
        called = []

        def callback(event):
            called.append(event.type)

        handler = FunctionEventHandler(callback, "test_handler")
        event = Event(EventType.APP_INITIALIZED)

        handler.handle(event)

        assert called == [EventType.APP_INITIALIZED]
        assert str(handler) == "FunctionEventHandler(test_handler)"

    @pytest.mark.asyncio
    async def test_async_function_event_handler(self):
        
        called = []

        async def callback(event):
            called.append(event.type)

        handler = AsyncFunctionEventHandler(callback, "test_handler")
        event = Event(EventType.APP_INITIALIZED)

        await handler.handle_async(event)

        assert called == [EventType.APP_INITIALIZED]
        assert str(handler) == "AsyncFunctionEventHandler(test_handler)"


class TestEventBus:
    

    def setup_method(self):
        
        self.event_bus = EventBus()

    def test_event_bus_initialization(self):
        
        assert self.event_bus._handlers == {}
        assert self.event_bus._filters == {}
        assert self.event_bus._recursion_depth == 0
        assert self.event_bus._max_recursion_depth == 10
        assert self.event_bus._async_enabled == True

    def test_subscribe_and_publish(self):
        
        called = []

        class TestHandler(EventHandler):
            def handle(self, event):
                called.append(event.type)

        handler = TestHandler()
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler)

        event = Event(EventType.APP_INITIALIZED)
        self.event_bus.publish(event)

        assert called == [EventType.APP_INITIALIZED]

    def test_unsubscribe(self):
        
        called = []

        class TestHandler(EventHandler):
            def handle(self, event):
                called.append(event.type)

        handler = TestHandler()
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler)
        self.event_bus.unsubscribe(EventType.APP_INITIALIZED, handler)

        event = Event(EventType.APP_INITIALIZED)
        self.event_bus.publish(event)

        assert called == []

    def test_publish_with_filter(self):
        
        called = []

        class TestHandler(EventHandler):
            def handle(self, event):
                called.append(event.type)

        handler = TestHandler()
        filter = EventTypeFilter(EventType.APP_INITIALIZED)
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler, filter)

        event1 = Event(EventType.APP_INITIALIZED)
        event2 = Event(EventType.GRID_UPDATED)

        self.event_bus.publish(event1)
        self.event_bus.publish(event2)

        assert called == [EventType.APP_INITIALIZED]

    def test_recursion_depth_limit(self):
        
        called = []

        class RecursiveHandler(EventHandler):
            def __init__(self, event_bus):
                self.event_bus = event_bus

            def handle(self, event):
                called.append(event.type)
                if len(called) < 15:
                    self.event_bus.publish(Event(event.type))

        handler = RecursiveHandler(self.event_bus)
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler)

        event = Event(EventType.APP_INITIALIZED)
        self.event_bus.publish(event)

        assert len(called) == 10

    def test_async_publish(self):
        
        called = []

        class AsyncTestHandler(AsyncEventHandler):
            async def handle_async(self, event):
                called.append(event.type)

        handler = AsyncTestHandler()
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler)

        event = Event(EventType.APP_INITIALIZED)

        async def run_test():
            await self.event_bus.publish_async(event)
            assert called == [EventType.APP_INITIALIZED]

        asyncio.run(run_test())

    def test_clear(self):
        
        class TestHandler(EventHandler):
            def handle(self, event):
                pass

        handler = TestHandler()
        self.event_bus.subscribe(EventType.APP_INITIALIZED, handler)

        assert self.event_bus.get_handler_count(EventType.APP_INITIALIZED) == 1

        self.event_bus.clear()

        assert self.event_bus.get_handler_count(EventType.APP_INITIALIZED) == 0

    def test_set_max_recursion_depth(self):
        
        self.event_bus.set_max_recursion_depth(5)
        assert self.event_bus._max_recursion_depth == 5

    def test_enable_async(self):
        
        self.event_bus.enable_async(False)
        assert not self.event_bus._async_enabled

        self.event_bus.enable_async(True)
        assert self.event_bus._async_enabled


class TestGlobalEventBus:
    

    def test_global_event_bus_exists(self):
        
        assert event_bus is not None
        assert isinstance(event_bus, EventBus)


if __name__ == "__main__":
    pytest.main([__file__])
