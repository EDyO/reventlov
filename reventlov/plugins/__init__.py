from future.utils import iteritems
import os
import logging
import importlib
import pkgutil

logger = logging.getLogger(__name__)


def iter_namespaces():
    return pkgutil.iter_modules(
        [os.path.dirname(__file__)],
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
        self.load_plugins()

    @property
    def disabled_plugins(self):
        disabled_plugins = os.getenv('REVENTLOV_DISABLED_PLUGINS')
        if disabled_plugins is None:
            return []
        return disabled_plugins.split(',')

    @property
    def enabled_plugins(self):
        return self.plugins.keys()

    @property
    def command_descs(self):
        command_help = {}
        for _, plugin in iteritems(self.plugins):
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

    def enable(self, plugin_name):
        module_name = f'reventlov.plugins.{plugin_name}'
        self.disabled_plugins.remove(plugin_name)
        bot = self.modules[module_name].Bot(self.dispatcher)
        self.plugins[plugin_name] = bot

    def load_plugins(self):
        for name in self.modules:
            plugin_name = name.split('.')[-1]
            if plugin_name not in self.disabled_plugins \
               and 'Bot' in dir(self.modules[name]):
                bot = self.modules[name].Bot(self.dispatcher)
                self.plugins[plugin_name] = bot

    def __iter__(self):
        return self.plugins.__iter__()

    def next(self):
        return self.plugins.next()

    def __getitem__(self, index):
        return self.plugins[index]
