import os
import logging
import importlib
import pkgutil

from reventlov.bot_plugin import BotPlugin

logger = logging.getLogger(__name__)


def find_bot(module):
    bot_class = None
    for attr_name in dir(module):
        if attr_name != 'BotPlugin':
            attr = getattr(module, attr_name)
            if type(attr) == type and issubclass(attr, BotPlugin):
                bot_class = attr
                break
    return bot_class


def get_list_from_environment(env_var_name):
    env_var_value = os.getenv(env_var_name)
    if env_var_value is None:
        return []
    return env_var_value.split(',')


def iter_namespaces():
    return pkgutil.iter_modules(
        [os.path.join(os.path.dirname(__file__), 'plugins')],
        'reventlov.plugins.',
    )


def import_plugin_modules():
    modules = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespaces()
    }
    return modules


class BotPlugins(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.modules = import_plugin_modules()
        self.plugins = {}
        self.__disabled_plugins()
        self.load_plugins()

    @property
    def disabled_plugins(self):
        return self.__disabled_plugins

    def __disabled_plugins(self, disabled_plugins=None):
        if disabled_plugins is None:
            self.__disabled_plugins = get_list_from_environment(
                'REVENTLOV_DISABLED_PLUGINS',
            )
        else:
            self.__disabled_plugins = disabled_plugins

    @property
    def enabled_plugins(self):
        return self.plugins.keys()

    @property
    def command_descs(self):
        command_help = {}
        for _, plugin in self.plugins.items():
            for handler in plugin.commands:
                command = f'/{handler.command[0]}'.replace('_', '\_')
                if handler.callback.__doc__ is None:
                    msg = 'Undefined command'
                else:
                    msg = handler.callback.__doc__.splitlines()[1].strip()
                command_help[command] = msg
        return command_help

    @property
    def feature_descs(self):
        return [
            self.plugins[plugin_name].__doc__.splitlines()[1].strip()
            for plugin_name in self.plugins
            if self.plugins[plugin_name].__doc__ is not None
        ]

    def disable(self, plugin_name):
        del self.plugins[plugin_name]
        self.disabled_plugins.append(plugin_name)

    def load_plugin(self, module_name):
        plugin_name = module_name.split('.')[-1]
        bot_class = find_bot(self.modules[module_name])
        if bot_class is None:
            logger.warning(f'No BotPlugin subclass found for {module_name}')
        else:
            bot = bot_class(self.dispatcher)
            self.plugins[plugin_name] = bot

    def enable(self, plugin_name):
        module_name = f'reventlov.plugins.{plugin_name}'
        del self.disabled_plugins[self.disabled_plugins.index(plugin_name)]
        self.load_plugin(module_name)

    def load_plugins(self):
        for module_name in self.modules:
            plugin_name = module_name.split('.')[-1]
            if plugin_name not in self.disabled_plugins:
                self.load_plugin(module_name)

    def __iter__(self):
        return self.plugins.__iter__()

    def next(self):
        return self.plugins.next()

    def __getitem__(self, index):
        return self.plugins[index]
