import os
import logging
import importlib
import pkgutil

logger = logging.getLogger(__name__)


def get_disabled_plugins():
    disabled_plugins = os.getenv('REVENTLOV_DISABLED_PLUGINS')
    if disabled_plugins is None:
        return []
    return disabled_plugins.split(',')


def add_plugin(plugin, dispatcher):
    disabled_plugins = get_disabled_plugins()
    os.environ['REVENTLOV_DISABLED_PLUGINS'] = ','.join([
        plugin_name
        for plugin_name in disabled_plugins
        if plugin != plugin_name
    ])
    logger.info(f'Enabling plugin {plugin}: {disabled_plugins}')
    return get_plugins(dispatcher)


def iter_namespaces():
    return pkgutil.iter_modules(
        [os.path.dirname(__file__)],
        'reventlov.plugins.',
    )


def find_plugins():
    excluded = get_disabled_plugins()
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
