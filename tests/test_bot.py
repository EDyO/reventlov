import os

import pytest
from reventlov.bot import Bot

example_bot_token = '343445268:31f983_134f98has_asdf9_q9dpheq09uro'
empty_bot_admins = ''
single_bot_admin = 'my_telegram_username'
multiple_bot_admins = 'my_telegram_username,another_telegram_username'
basic_commands = [
    'start',
    'help',
    'settings',
    'disable_plugin',
    'enable_plugin',
]
bot_test_cases = [
    (
        {
            'TELEGRAM_BOT_TOKEN': example_bot_token,
            'TELEGRAM_BOT_ADMINS': empty_bot_admins,
        },
        {
            'admins': [''],
            'commands': basic_commands,
        },
    ),
    (
        {
            'TELEGRAM_BOT_TOKEN': example_bot_token,
            'TELEGRAM_BOT_ADMINS': single_bot_admin,
        },
        {
            'admins': ['my_telegram_username'],
            'commands': basic_commands,
        },
    ),
    (
        {
            'TELEGRAM_BOT_TOKEN': example_bot_token,
            'TELEGRAM_BOT_ADMINS': multiple_bot_admins,
        },
        {
            'admins': ['my_telegram_username', 'another_telegram_username'],
            'commands': basic_commands,
        },
    ),
]


class Updater(object):
    def __init__(self, *args, **kwargs):
        self.dispatcher = Dispatcher()


class Dispatcher(object):
    def __init__(self):
        self.registered_handlers = []

    def add_handler(self, handler):
        self.registered_handlers.append(handler.command[0])


@pytest.mark.parametrize('environ, expected', bot_test_cases)
def test_bot_creation(mocker, environ, expected):
    mocker.patch.dict(os.environ, environ)
    mocker.patch('reventlov.bot.Updater', new=lambda *a, **kw: Updater(a, kw))
    bot_plugins = mocker.patch('reventlov.bot.BotPlugins')

    bot = Bot()

    assert bot.admins == expected['admins']
    commands = [handler for handler in bot.dispatcher.registered_handlers]
    assert len(commands) == len(expected['commands'])
    for command in commands:
        assert command in expected['commands']
    bot_plugins.assert_called_once_with(bot.dispatcher)
