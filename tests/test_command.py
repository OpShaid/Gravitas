import pytest
from unittest.mock import Mock, MagicMock
from plugins.command import Command


class TestCommand:
    

    def setup_method(self):
        
        self.mock_controller = Mock()
        self.mock_controller.reset_view = Mock(return_value=None)
        self.mock_controller.toggle_grid = Mock(return_value=None)
        self.mock_controller.clear_grid = Mock(return_value=None)
        self.mock_controller.switch_vector_field_direction = Mock(return_value=None)
        def mock_set_speed(speed):
            return "Speed set to 10"
        def mock_set_gravity(gravity):
            return 0.5
        def mock_add_marker(x, y):
            pass

        self.mock_controller.set_speed = Mock(side_effect=mock_set_speed)
        self.mock_controller.set_gravity = Mock(side_effect=mock_set_gravity)
        self.mock_controller.add_marker = Mock(side_effect=mock_add_marker)

        # Set signatures for mock methods to match expected parameter counts
        import inspect
        self.mock_controller.set_speed.__signature__ = inspect.signature(mock_set_speed)
        self.mock_controller.set_gravity.__signature__ = inspect.signature(mock_set_gravity)
        self.mock_controller.add_marker.__signature__ = inspect.signature(mock_add_marker)

        import tempfile
        import json
        import os

        commands_data = {
            "commands": {
                "reset_view": "reset_view",
                "toggle_grid": "toggle_grid",
                "clear_grid": "clear_grid",
                "switch_direction": "switch_vector_field_direction",
                "set_speed": "set_speed",
                "set_gravity": "set_gravity",
                "add_marker": "add_marker"
            },
            "descriptions": {
                "reset_view": "reset viewtostate",
                "toggle_grid": "toggle grid show",
                "clear_grid": "clear gridin",
                "switch_direction": "togglevector fielddirection",
                "set_speed": "setparticlevelocity (param: speed)",
                "set_gravity": "setgravityvalue (param: gravity)",
                "add_marker": "addmarker (param: x, y)"
            },
            "no_param_commands": [
                "reset_view",
                "toggle_grid",
                "clear_grid",
                "switch_direction"
            ]
        }

        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(commands_data, self.temp_file)
        self.temp_file.close()

        self.command = Command(self.mock_controller, self.temp_file.name)

    def test_execute_reset_view(self):
        
        result = self.command.execute("reset_view")
        assert result == "command 'reset_view' executesuccess"
        self.mock_controller.reset_view.assert_called_once()

    def test_execute_toggle_grid(self):
        
        result = self.command.execute("toggle_grid")
        assert result == "command 'toggle_grid' executesuccess"
        self.mock_controller.toggle_grid.assert_called_once()

    def test_execute_clear_grid(self):
        
        result = self.command.execute("clear_grid")
        assert result == "command 'clear_grid' executesuccess"
        self.mock_controller.clear_grid.assert_called_once()

    def test_execute_switch_direction(self):
        
        result = self.command.execute("switch_direction")
        assert result == "command 'switch_direction' executesuccess"
        self.mock_controller.switch_vector_field_direction.assert_called_once()

    def test_execute_unknown_command(self):
        
        result = self.command.execute("unknown_command")
        assert "error: command 'unknown_command'" in result
        assert " 'help' instructionallsupportinstruction。" in result

    def test_execute_empty_command(self):
        
        result = self.command.execute("")
        assert result == "error: command is empty"

    def test_execute_whitespace_command(self):
        
        result = self.command.execute("   ")
        assert result == "error: command is empty"

    def test_execute_command_with_extra_args(self):
        
        result = self.command.execute("reset_view extra arg")
        assert result == "error: command 'reset_view' not supportparam"
        self.mock_controller.reset_view.assert_not_called()

    def test_execute_case_insensitive(self):
        
        result = self.command.execute("RESET_VIEW")
        assert result == "command 'reset_view' executesuccess"
        self.mock_controller.reset_view.assert_called_once()

    def test_execute_with_exception(self):
        
        self.mock_controller.reset_view.side_effect = Exception("Test exception")
        result = self.command.execute("reset_view")
        assert "error: executecommand 'reset_view' hourexception: Exception: Test exception" in result

    def test_list_commands(self):
        
        result = self.command.list_commands()
        assert "availablecommand:" in result
        assert "reset_view (param): reset viewtostate" in result
        assert "toggle_grid (param): toggle grid show" in result
        assert "clear_grid (param): clear gridin" in result
        assert "switch_direction (param): togglevector fielddirection" in result
        assert "set_speed (need 1 param): setparticlevelocity (param: speed)" in result

    def test_commands_dict_structure(self):
        
        expected_commands = ['reset_view', 'toggle_grid', 'clear_grid', 'switch_direction', 'set_speed', 'set_gravity', 'add_marker', 'help']
        assert list(self.command.commands.keys()) == expected_commands
        for cmd in expected_commands:
            assert callable(self.command.commands[cmd])

    def test_execute_command_with_unsupported_args(self):
        
        result = self.command.execute("reset_view arg1 arg2")
        assert "error: command 'reset_view' not supportparam" in result

    def test_execute_with_specific_exception(self):
        
        self.mock_controller.reset_view.side_effect = ValueError("Invalid value")
        result = self.command.execute("reset_view")
        assert "error: executecommand 'reset_view' hourexception: ValueError: Invalid value" in result

    def test_register_command(self):
        
        def new_command():
            pass
        self.command.register_command('new_cmd', new_command, 'commanddescription')
        assert 'new_cmd' in self.command.commands
        assert self.command.commands['new_cmd'] == new_command
        assert self.command.descriptions['new_cmd'] == 'commanddescription'
        result = self.command.execute("new_cmd")
        assert result == "command 'new_cmd' executesuccess"

    def test_execute_command_with_int_args(self):
        
        result = self.command.execute("set_speed 10")
        assert result == "command 'set_speed' executesuccess，: Speed set to 10"
        self.mock_controller.set_speed.assert_called_once_with(10)

    def test_execute_command_with_float_args(self):
        
        result = self.command.execute("set_gravity 0.5")
        assert result == "command 'set_gravity' executesuccess，: 0.5"
        self.mock_controller.set_gravity.assert_called_once_with(0.5)

    def test_execute_command_with_multiple_args(self):
        
        result = self.command.execute("add_marker 100 200")
        assert result == "command 'add_marker' executesuccess"
        self.mock_controller.add_marker.assert_called_once_with(100, 200)

    def test_execute_command_with_string_args(self):
        
        result = self.command.execute("set_speed hello")
        assert result == "command 'set_speed' executesuccess，: Speed set to 10"
        self.mock_controller.set_speed.assert_called_once_with("hello")

    def test_execute_command_with_too_many_args(self):
        
        result = self.command.execute("set_speed 10 20")
        assert "error: command 'set_speed'  1 param， 2 " in result
        self.mock_controller.set_speed.assert_not_called()

    def test_execute_command_with_too_few_args(self):
        
        result = self.command.execute("add_marker 100")
        assert "error: command 'add_marker'  2 param， 1 " in result
        self.mock_controller.add_marker.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
