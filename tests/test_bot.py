import os

import pytest
from reventlov.bot import Bot

example_bot_token = '343445268:31f983_134f98has_asdf9_q9dpheq09uro'
empty_bot_admins_env_value = ''
single_bot_admin_env_value = 'my_telegram_username'
multiple_bot_admins_env_value = 'my_telegram_username,' \
                                'another_telegram_username'
many_admins = [
    'my_telegram_username',
    'another_telegram_username',
]
basic_commands = [
    'start',
    'help',
    'settings',
    'disable_plugin',
    'enable_plugin',
]
pomodoro_plugin = 'pomodoro'
pomodoro_feature_desc = 'I can handle alarms'
trello_plugin = 'trello'
trello_feature_desc = 'I can handle Trello cards'
bot_test_cases = {
    'tests': [
        (
            {
                'TELEGRAM_BOT_TOKEN': example_bot_token,
                'TELEGRAM_BOT_ADMINS': empty_bot_admins_env_value,
            },
            [],
            [],
            {
                'admins': [''],
                'commands': basic_commands,
                'enabled_plugins': '',
            },
        ),
        (
            {
                'TELEGRAM_BOT_TOKEN': example_bot_token,
                'TELEGRAM_BOT_ADMINS': single_bot_admin_env_value,
            },
            [pomodoro_plugin],
            [pomodoro_feature_desc],
            {
                'admins': ['my_telegram_username'],
                'commands': basic_commands,
                'enabled_plugins': 'pomodoro',
            },
        ),
        (
            {
                'TELEGRAM_BOT_TOKEN': example_bot_token,
                'TELEGRAM_BOT_ADMINS': multiple_bot_admins_env_value,
            },
            [pomodoro_plugin],
            [pomodoro_feature_desc],
            {
                'admins': many_admins,
                'commands': basic_commands,
                'enabled_plugins': pomodoro_plugin,
            },
        ),
        (
            {
                'TELEGRAM_BOT_TOKEN': example_bot_token,
                'TELEGRAM_BOT_ADMINS': multiple_bot_admins_env_value,
            },
            [pomodoro_plugin, trello_plugin],
            [pomodoro_feature_desc, trello_feature_desc],
            {
                'admins': many_admins,
                'commands': basic_commands,
                'enabled_plugins': 'pomodoro, trello',
            },
        ),
    ],
    'ids': [
        'No admin no plugins',
        'Single admin one plugin',
        'Many admins one plugin',
        'Many admins many plugins',
    ]
}


class Updater(object):
    def __init__(self, *args, **kwargs):
        self.dispatcher = Dispatcher()
        self.bot = BotInterface()
        self.polling = False

    def start_polling(self):
        self.polling = not self.polling


class Dispatcher(object):
    def __init__(self):
        self.registered_handlers = []

    def add_handler(self, handler):
        self.registered_handlers.append(handler.command[0])


class BotInterface(object):
    def get_me(self):
        return {
            'first_name': 'R. Giskard Reventlov',
            'username': 'reventlovbot',
        }


class Logger(object):
    def __init__(self):
        self.__info = []

    def info(self, message):
        self.__info.append(message)

    @property
    def messages(self):
        messages = []
        messages.extend(self.__info)
        return messages


@pytest.mark.parametrize(
    'environ, present_plugins, feature_descs, expected',
    bot_test_cases['tests'],
    ids=bot_test_cases['ids'],
)
def test_bot(mocker, environ, present_plugins, feature_descs, expected):
    mocker.patch.dict(os.environ, environ)
    mocker.patch(
        'reventlov.bot.Updater',
        new=lambda *a, **kw: Updater(a, kw),
    )
    bot_plugins = mocker.patch(
        'reventlov.bot.BotPlugins',
        spec=True,
        enabled_plugins=present_plugins,
        feature_descs=feature_descs,
    )
    logger = Logger()
    mocker.patch(
        'reventlov.bot.logger',
        new=logger,
    )

    bot = Bot()
    bot.run()

    assert bot.admins == expected['admins']
    commands = [handler for handler in bot.dispatcher.registered_handlers]
    assert len(commands) == len(expected['commands'])
    for command in commands:
        assert command in expected['commands']
    bot_plugins.assert_called_once_with(bot.dispatcher)
    assert bot.enabled_plugins == expected['enabled_plugins']
    assert bot.updater.polling
    greeting = 'I am R. Giskard Reventlov (@reventlovbot)'
    assert greeting in logger.messages
    start_text = f'{greeting}'
    for feature_desc in feature_descs:
        start_text = f'{start_text}\n- {feature_desc}'
    assert start_text == bot.start_message
    help_msg = bot.help_message
    assert len(help_msg.splitlines()) == 4
    assert '-/start' in help_msg
    assert '-/help' in help_msg
    assert '-/settings' in help_msg
