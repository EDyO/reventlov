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


def find_plugins():
    excluded = (os.getenv('REVENTLOV_DISABLED_PLUGINS') or '').split(',')
    plugins = {
        name.split('.')[-1]: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespaces()
        if name.split('.')[-1] not in excluded
    }
    for plugin in excluded:
        plugins[plugin] = None
    return plugins


def get_plugins(dispatcher):
    plugins = find_plugins()
    for name in plugins:
        if plugins[name] is not None:
            if 'Bot' in dir(plugins[name]):
                plugins[name] = plugins[name].Bot(dispatcher)
            else:
                logger.warn(
                    f'Plugin {name} does not provide Bot class'
                )
    return plugins
