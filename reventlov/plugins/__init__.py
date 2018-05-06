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


plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in iter_namespaces()
}


def get_plugins(dispatcher):
    plugin_dict = {}
    for name in plugins:
        if 'Bot' in dir(plugins[name]):
            plugin_dict[name] = plugins[name].Bot(dispatcher)
        else:
            logger.warn("Plugin {} does not provide Bot class".format(name))
    return plugin_dict
