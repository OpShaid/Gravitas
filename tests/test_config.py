import pytest
import json
import os
from gravitas.core.config import ConfigManager


class TestConfigManager:
    

    def setup_method(self):
        
        self.config_file = "test_config.json"
        self.manager = ConfigManager(self.config_file)
        self.manager.reset_to_default()

    def teardown_method(self):
        
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_load_config(self):
        
        config_data = {
            "grid": {"width": 640, "height": 480},
            "vector": {"scale": 1.0}
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)

        self.manager.load_config()
        assert self.manager.get("grid.width") == 640
        assert self.manager.get("vector.scale") == 1.0

    def test_save_config(self):
        
        self.manager.set("test_key", "test_value")
        self.manager.save_config()

        with open(self.config_file, 'r') as f:
            data = json.load(f)

        assert data.get("test_key") == "test_value"

    def test_get_set(self):
        
        self.manager.set("test.value", 42)
        assert self.manager.get("test.value") == 42
        assert self.manager.get("nonexistent", "default") == "default"

    def test_nested_access(self):
        
        self.manager.set("nested.deep.value", "test")
        assert self.manager.get("nested.deep.value") == "test"

    def test_validation(self):
        
        # testtypeverify
        assert self.manager.set("grid_width", 800)
        assert not self.manager.set("grid_width", "invalid")

        assert self.manager.set("vector_scale", 2.0)
        assert not self.manager.set("vector_scale", 15.0)

        assert self.manager.set("vector_color", [1.0, 0.5, 0.0])
        assert not self.manager.set("vector_color", "invalid")

    def test_event_publishing(self):
        
        old_value = self.manager.get("grid_width")
        self.manager.set("grid_width", old_value + 100)

    def test_dynamic_registration(self):
        
        assert self.manager.set("custom_option", "value")
        assert self.manager.get("custom_option") == "value"

    def test_reset_to_default(self):
        
        original_value = self.manager.get("grid_width")
        self.manager.set("grid_width", original_value + 100)
        assert self.manager.get("grid_width") == original_value + 100

        self.manager.reset_to_default("grid_width")
        assert self.manager.get("grid_width") == original_value

    def test_get_option_info(self):
        
        info = self.manager.get_option_info("grid_width")
        assert info is not None
        assert info["type"] == "number"
        assert info["description"] == "gridwidth"

    def test_invalid_config_file(self):
        
        invalid_file = "invalid_config.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json")

        manager = ConfigManager(invalid_file)

        if os.path.exists(invalid_file):
            os.remove(invalid_file)


if __name__ == "__main__":
    pytest.main([__file__])
