import pytest
import time
from unittest.mock import Mock
from gravitas.core.state import StateManager, StateChange, state_manager


class TestStateChange:
    

    def test_state_change_creation(self):
        
        change = StateChange("test_key", "old_value", "new_value", 1234567890.0)

        assert change.key == "test_key"
        assert change.old_value == "old_value"
        assert change.new_value == "new_value"
        assert change.timestamp == 1234567890.0

    def test_state_change_to_dict(self):
        
        change = StateChange("test_key", "old", "new", 1234567890.0)
        data = change.to_dict()

        assert data["key"] == "test_key"
        assert data["old_value"] == "old"
        assert data["new_value"] == "new"
        assert data["timestamp"] == 1234567890.0


class TestStateManager:
    

    def setup_method(self):
        
        self.manager = StateManager()

    def test_state_manager_initialization(self):
        
        assert self.manager._state == {}
        assert self.manager._listeners == {}
        assert self.manager._change_history == []
        assert self.manager._max_history_size == 100

    def test_get_set(self):
        
        self.manager.set("test_key", "test_value")
        assert self.manager.get("test_key") == "test_value"

        # testdefault value
        assert self.manager.get("nonexistent", "default") == "default"

    def test_set_without_notify(self):
        
        called = []

        def listener(key, old, new):
            called.append((key, old, new))

        self.manager.add_listener("test_key", listener)

        self.manager.set("test_key", "value1", notify=False)
        assert called == []

        self.manager.set("test_key", "value2", notify=True)
        assert called == [("test_key", "value1", "value2")]

    def test_update(self):
        
        updates = {"key1": "value1", "key2": "value2"}
        self.manager.update(updates)

        assert self.manager.get("key1") == "value1"
        assert self.manager.get("key2") == "value2"

    def test_remove(self):
        
        self.manager.set("test_key", "test_value")
        assert self.manager.remove("test_key")
        assert self.manager.get("test_key") is None

        assert not self.manager.remove("nonexistent")

    def test_clear(self):
        
        self.manager.set("key1", "value1")
        self.manager.set("key2", "value2")

        self.manager.clear()

        assert self.manager.get("key1") is None
        assert self.manager.get("key2") is None

    def test_get_all(self):
        
        self.manager.set("key1", "value1")
        self.manager.set("key2", "value2")

        all_state = self.manager.get_all()
        assert all_state == {"key1": "value1", "key2": "value2"}

    def test_contains(self):
        
        self.manager.set("test_key", "value")
        assert self.manager.contains("test_key")
        assert not self.manager.contains("nonexistent")

    def test_add_remove_listener(self):
        
        called = []

        def listener(key, old, new):
            called.append((key, old, new))

        # addlistener
        self.manager.add_listener("test_key", listener)
        assert listener in self.manager._listeners["test_key"]

        self.manager.set("test_key", "value")
        assert called == [("test_key", None, "value")]

        # removelistener
        self.manager.remove_listener("test_key", listener)
        assert listener not in self.manager._listeners["test_key"]

        called.clear()
        self.manager.set("test_key", "new_value")
        assert called == []

    def test_get_change_history(self):
        
        self.manager.set("key1", "value1")
        self.manager.set("key2", "value2")
        self.manager.set("key1", "new_value1")

        history = self.manager.get_change_history()
        assert len(history) == 3

        key1_history = self.manager.get_change_history("key1")
        assert len(key1_history) == 2
        assert key1_history[0].old_value is None
        assert key1_history[0].new_value == "value1"
        assert key1_history[1].old_value == "value1"
        assert key1_history[1].new_value == "new_value1"

        limited_history = self.manager.get_change_history(limit=1)
        assert len(limited_history) == 1

    def test_create_restore_snapshot(self):
        
        self.manager.set("key1", "value1")
        self.manager.set("key2", "value2")

        # createsnapshot
        snapshot = self.manager.create_snapshot()
        assert snapshot["state"] == {"key1": "value1", "key2": "value2"}
        assert isinstance(snapshot["timestamp"], float)

        self.manager.set("key1", "modified")

        # restoresnapshot
        self.manager.restore_snapshot(snapshot)
        assert self.manager.get("key1") == "value1"
        assert self.manager.get("key2") == "value2"

    def test_context_manager(self):
        
        with self.manager:
            assert self.manager._nested_level == 1

            with self.manager:
                assert self.manager._nested_level == 2

            assert self.manager._nested_level == 1

        assert self.manager._nested_level == 0

    def test_magic_methods(self):
        
        self.manager["test_key"] = "test_value"
        assert self.manager["test_key"] == "test_value"

        # __delitem__
        del self.manager["test_key"]
        assert self.manager.get("test_key") is None

        # __contains__
        self.manager.set("test_key", "value")
        assert "test_key" in self.manager
        assert "nonexistent" not in self.manager

        # __len__
        assert len(self.manager) == 1

        # __iter__
        keys = list(self.manager)
        assert keys == ["test_key"]

    def test_listener_exception_handling(self):
        
        def failing_listener(key, old, new):
            raise Exception("Test exception")

        def working_listener(key, old, new):
            working_listener.called = True

        working_listener.called = False

        self.manager.add_listener("test_key", failing_listener)
        self.manager.add_listener("test_key", working_listener)

        self.manager.set("test_key", "value")

        assert working_listener.called

    def test_history_size_limit(self):
        
        self.manager._max_history_size = 2

        for i in range(5):
            self.manager.set(f"key{i}", f"value{i}")

        history = self.manager.get_change_history()
        assert len(history) == 2


class TestGlobalStateManager:
    

    def test_global_state_manager_exists(self):
        
        assert state_manager is not None
        assert isinstance(state_manager, StateManager)


if __name__ == "__main__":
    pytest.main([__file__])
