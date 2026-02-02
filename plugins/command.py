
from typing import Optional
import inspect
import json
import os
import logging
from gravitas.input import input_handler, KeyMap


class Command:
    def __init__(self, controller, commands_file=None):
        self.controller = controller
        if commands_file is None:
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            commands_file = os.path.join(plugin_dir, 'commands.json')
        self.commands_file = commands_file
        self.commands = {}
        self.descriptions = {}
        self.no_param_commands = set()
        self.logger = logging.getLogger(__name__)
        self._load_commands()
      
        self.register_command('help', self.list_commands, 'showallavailableinstruction', no_param=True)

    def _load_commands(self):
        
        if not os.path.exists(self.commands_file):
            raise FileNotFoundError(f"Commands file '{self.commands_file}' not found.")
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            commands_data = data.get('commands', {})
            descriptions_data = data.get('descriptions', {})
            no_param_commands = data.get('no_param_commands', [])
            for cmd, method_str in commands_data.items():
                try:
                    method = getattr(self.controller, method_str.split('.')[-1])
                    self.commands[cmd] = method
                    self.descriptions[cmd] = descriptions_data.get(cmd, 'description')
                    self.logger.info(f"Loaded command '{cmd}' -> {method_str}")
                except AttributeError as e:
                    self.logger.error(f"Failed to load command '{cmd}': method '{method_str}' not found on controller. Skipping.")
            self.no_param_commands = set(no_param_commands)
            self.logger.info(f"Loaded {len(self.commands)} commands, {len(self.no_param_commands)} no-param commands.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing commands from '{self.commands_file}': {e}")

    def _convert_arg(self, arg_str: str):
        
        try:
            if arg_str.isdigit() or (arg_str.startswith('-') and arg_str[1:].isdigit()):
                return int(arg_str)
            float_val = float(arg_str)
            return float_val
        except ValueError:
            pass
    
        return arg_str

    def execute(self, command_str: str) -> str:
        
        parts = command_str.strip().split()
        if not parts:
            return "error: commandis empty"

        cmd = parts[0].lstrip('/').lower()
        if cmd not in self.commands:
            return f"error: command '{cmd}'。 'help' instructionallsupportinstruction。"

        args = parts[1:]  
        try:
            func = self.commands[cmd]
            sig = inspect.signature(func)
            param_count = len(sig.parameters)

            if len(args) > 0:
                if cmd in self.no_param_commands:
                    return f"error: command '{cmd}' not supportparam"
                if param_count == 0:
                    return f"error: command '{cmd}' not supportparam"
                if len(args) > param_count:
                    return f"error: command '{cmd}'  {param_count} param， {len(args)} "
                if len(args) < param_count:
                    return f"error: command '{cmd}'  {param_count} param， {len(args)} "
            
                converted_args = [self._convert_arg(arg) for arg in args]
                result = func(*converted_args)
                self.logger.info(f"Executed command '{cmd}' with args {converted_args}")
            else:
                if param_count > 0 and cmd not in self.no_param_commands:
                    return f"error: command '{cmd}' needparam"
                result = func()
                self.logger.info(f"Executed command '{cmd}' without args")

            if result is not None:
                return f"command '{cmd}' executesuccess，: {result}"
            else:
                return f"command '{cmd}' executesuccess"
        except Exception as e:
            self.logger.error(f"Error executing command '{cmd}': {e}")
            return f"error: executecommand '{cmd}' hourexception: {type(e).__name__}: {e}"

    def list_commands(self) -> str:
        
        lines = ["availablecommand:"]
        for cmd in self.commands.keys():
            desc = self.descriptions.get(cmd, "description")
            param_info = ""
            if cmd in self.no_param_commands:
                param_info = " (param)"
            else:
                sig = inspect.signature(self.commands[cmd])
                param_count = len(sig.parameters)
                if param_count > 0:
                    param_info = f" (need {param_count} param)"
                else:
                    param_info = " (param)"
            lines.append(f"- {cmd}{param_info}: {desc}")
        return "\n".join(lines)

    def register_command(self, cmd, method, description, no_param=False):
        
        self.commands[cmd] = method
        self.descriptions[cmd] = description
        if no_param:
            self.no_param_commands.add(cmd)
        self.logger.info(f"Registered new command '{cmd}' (no_param: {no_param})")


class CommandInputHandler:
    

    def __init__(self, command_plugin, history_file='plugins/command_history.json'):
        self.command_plugin = command_plugin
        self.command_mode = False
        self.command_string = ""
        self.cursor_pos = 0
        self.was_pressed = {}
        self.history_file = history_file
        self.history = []
        self.history_index = -1
        self.logger = logging.getLogger(__name__)
        self._load_history()

    def _load_history(self):
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self.logger.info(f"Loaded {len(self.history)} commands from history")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to load command history: {e}")
                self.history = []
        else:
            self.history = []

    def _save_history(self):
        
        try:
            max_history = 100
            if len(self.history) > max_history:
                self.history = self.history[-max_history:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            self.logger.error(f"Failed to save command history: {e}")

    def toggle_command_mode(self):
        
        if not self.command_mode:
            self.command_mode = True
            self.command_string = ""
            self.cursor_pos = 0
            print("[instruction] activated - inputinstructionbackpress Enterexecute，press ESCcancel")
        else:
            self.command_mode = False
            print("[instruction] exited")

    def get_toggle_callback(self):
        
        return self.toggle_command_mode

    def _display_command(self):
        
        print("\033[?25l", end='', flush=True) 
        print(f"\r\033[K[instructioninput] {self.command_string}", end='', flush=True)
        if self.cursor_pos < len(self.command_string):
            move_left = len(self.command_string) - self.cursor_pos
            print(f"\033[{move_left}D", end='', flush=True)
        print("\033[?25h", end='', flush=True)  

    def _handle_command_input(self):
        
        key_to_char = {
            KeyMap.A: 'a', KeyMap.B: 'b', KeyMap.C: 'c', KeyMap.D: 'd', KeyMap.E: 'e',
            KeyMap.F: 'f', KeyMap.G: 'g', KeyMap.H: 'h', KeyMap.I: 'i', KeyMap.J: 'j',
            KeyMap.K: 'k', KeyMap.L: 'l', KeyMap.M: 'm', KeyMap.N: 'n', KeyMap.O: 'o',
            KeyMap.P: 'p', KeyMap.Q: 'q', KeyMap.R: 'r', KeyMap.S: 's', KeyMap.T: 't',
            KeyMap.U: 'u', KeyMap.V: 'v', KeyMap.W: 'w', KeyMap.X: 'x', KeyMap.Y: 'y',
            KeyMap.Z: 'z',
            KeyMap._0: '0', KeyMap._1: '1', KeyMap._2: '2', KeyMap._3: '3', KeyMap._4: '4',
            KeyMap._5: '5', KeyMap._6: '6', KeyMap._7: '7', KeyMap._8: '8', KeyMap._9: '9',
            KeyMap.SPACE: ' ',
            KeyMap.MINUS: '-',
            KeyMap.EQUAL: '=',
            KeyMap.SEMICOLON: ';',
            KeyMap.APOSTROPHE: "'",
            KeyMap.COMMA: ',',
            KeyMap.PERIOD: '.',
            KeyMap.SLASH: '/',
            KeyMap.KP_0: '0', KeyMap.KP_1: '1', KeyMap.KP_2: '2', KeyMap.KP_3: '3',
            KeyMap.KP_4: '4', KeyMap.KP_5: '5', KeyMap.KP_6: '6', KeyMap.KP_7: '7',
            KeyMap.KP_8: '8', KeyMap.KP_9: '9',
            KeyMap.KP_DECIMAL: '.',
            KeyMap.KP_DIVIDE: '/',
            KeyMap.KP_MULTIPLY: '*',
            KeyMap.KP_SUBTRACT: '-',
            KeyMap.KP_ADD: '+',
        }

        shifted_key_to_char = {
            KeyMap.A: 'A', KeyMap.B: 'B', KeyMap.C: 'C', KeyMap.D: 'D', KeyMap.E: 'E',
            KeyMap.F: 'F', KeyMap.G: 'G', KeyMap.H: 'H', KeyMap.I: 'I', KeyMap.J: 'J',
            KeyMap.K: 'K', KeyMap.L: 'L', KeyMap.M: 'M', KeyMap.N: 'N', KeyMap.O: 'O',
            KeyMap.P: 'P', KeyMap.Q: 'Q', KeyMap.R: 'R', KeyMap.S: 'S', KeyMap.T: 'T',
            KeyMap.U: 'U', KeyMap.V: 'V', KeyMap.W: 'W', KeyMap.X: 'X', KeyMap.Y: 'Y',
            KeyMap.Z: 'Z',
            KeyMap._0: ')', KeyMap._1: '!', KeyMap._2: '@', KeyMap._3: '#', KeyMap._4: '$',
            KeyMap._5: '%', KeyMap._6: '^', KeyMap._7: '&', KeyMap._8: '*', KeyMap._9: '(',
            KeyMap.MINUS: '_',
            KeyMap.EQUAL: '+',
            KeyMap.SEMICOLON: ':',
            KeyMap.APOSTROPHE: '"',
            KeyMap.COMMA: '<',
            KeyMap.PERIOD: '>',
            KeyMap.SLASH: '?',
            KeyMap.KP_0: '0', KeyMap.KP_1: '1', KeyMap.KP_2: '2', KeyMap.KP_3: '3',
            KeyMap.KP_4: '4', KeyMap.KP_5: '5', KeyMap.KP_6: '6', KeyMap.KP_7: '7',
            KeyMap.KP_8: '8', KeyMap.KP_9: '9',
            KeyMap.KP_DECIMAL: '.',
            KeyMap.KP_DIVIDE: '/',
            KeyMap.KP_MULTIPLY: '*',
            KeyMap.KP_SUBTRACT: '-',
            KeyMap.KP_ADD: '+',
        }

        if input_handler.is_key_pressed(KeyMap.ENTER):
            if not self.was_pressed.get(KeyMap.ENTER, False):
                self._execute_command()
            self.was_pressed[KeyMap.ENTER] = True
        else:
            self.was_pressed[KeyMap.ENTER] = False

        if input_handler.is_key_pressed(KeyMap.ESCAPE):
            if not self.was_pressed.get(KeyMap.ESCAPE, False):
                self.command_mode = False
                print("\n[instruction] exited")
            self.was_pressed[KeyMap.ESCAPE] = True
        else:
            self.was_pressed[KeyMap.ESCAPE] = False

        if input_handler.is_key_pressed(KeyMap.BACKSPACE):
            if not self.was_pressed.get(KeyMap.BACKSPACE, False) and self.cursor_pos > 0:
                self.command_string = self.command_string[:self.cursor_pos-1] + self.command_string[self.cursor_pos:]
                self.cursor_pos -= 1
                self._display_command()
            self.was_pressed[KeyMap.BACKSPACE] = True
        else:
            self.was_pressed[KeyMap.BACKSPACE] = False

        if input_handler.is_key_pressed(KeyMap.UP):
            if not self.was_pressed.get(KeyMap.UP, False) and self.history:
                if self.history_index == -1:
                    self.temp_command = self.command_string
                self.history_index = min(self.history_index + 1, len(self.history) - 1)
                self.command_string = self.history[len(self.history) - 1 - self.history_index]
                self.cursor_pos = len(self.command_string)
                self._display_command()
            self.was_pressed[KeyMap.UP] = True
        else:
            self.was_pressed[KeyMap.UP] = False

        if input_handler.is_key_pressed(KeyMap.DOWN):
            if not self.was_pressed.get(KeyMap.DOWN, False) and self.history:
                self.history_index = max(self.history_index - 1, -1)
                if self.history_index == -1:
                    self.command_string = getattr(self, 'temp_command', "")
                else:
                    self.command_string = self.history[len(self.history) - 1 - self.history_index]
                self.cursor_pos = len(self.command_string)
                self._display_command()
            self.was_pressed[KeyMap.DOWN] = True
        else:
            self.was_pressed[KeyMap.DOWN] = False

        if input_handler.is_key_pressed(KeyMap.LEFT):
            if not self.was_pressed.get(KeyMap.LEFT, False):
                self.cursor_pos = max(0, self.cursor_pos - 1)
                self._display_command()
            self.was_pressed[KeyMap.LEFT] = True
        else:
            self.was_pressed[KeyMap.LEFT] = False

        if input_handler.is_key_pressed(KeyMap.RIGHT):
            if not self.was_pressed.get(KeyMap.RIGHT, False):
                self.cursor_pos = min(len(self.command_string), self.cursor_pos + 1)
                self._display_command()
            self.was_pressed[KeyMap.RIGHT] = True
        else:
            self.was_pressed[KeyMap.RIGHT] = False

        in_quotes = False
        quote_char = None
        shift_pressed = input_handler.is_key_pressed(KeyMap.LEFT_SHIFT) or input_handler.is_key_pressed(KeyMap.RIGHT_SHIFT)
        for key, char in key_to_char.items():
            if input_handler.is_key_pressed(key):
                if not self.was_pressed.get(key, False):
                    char_map = shifted_key_to_char if shift_pressed else key_to_char
                    char = char_map.get(key, char)
                    if char in ('"', "'") and (not in_quotes or char == quote_char):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        else:
                            in_quotes = False
                            quote_char = None
                    self.command_string = self.command_string[:self.cursor_pos] + char + self.command_string[self.cursor_pos:]
                    self.cursor_pos += 1
                    self._display_command()
                self.was_pressed[key] = True
            else:
                self.was_pressed[key] = False

    def _execute_command(self):
        
        if not self.command_string.strip():
            print("\n[instruction] instructionis empty")
            self.command_mode = False
            return

        print(f"\n[instruction] execute: {self.command_string}")
        result = self.command_plugin.execute(self.command_string)
        print(f"[instruction] : {result}")

        if not result.startswith("error"):
            if not self.history or self.history[-1] != self.command_string:
                self.history.append(self.command_string)
                self._save_history()

        self.history_index = -1
        if hasattr(self, 'temp_command'):
            delattr(self, 'temp_command')

        self.command_mode = False
