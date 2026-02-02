# Plugin manager - dynamic loading and management
import importlib
import os

# loaded plugins storage
_plugins = {}

def _load_plugins():
    # get plugins directory
    plugins_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')

    # iterate through all .py files in plugins dir
    for file in os.listdir(plugins_dir):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]  # remove .py extension
            try:
                # dynamicaly import plugin module
                module = importlib.import_module(f'plugins.{module_name}')
                # add all public objects to plugins dict
                _plugins.update({name: obj for name, obj in vars(module).items()
                               if not name.startswith('_')})
            except ImportError as e:
                print(f"[Warning] Failed to load plugin {module_name}: {e}")

# load plugins
_load_plugins()

def __getattr__(name):
    # module level getattr for direct plugin imports
    if name in _plugins:
        return _plugins[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def get_plugin(name):
    return __getattr__(name)

def list_plugins():
    return list(_plugins.keys())
