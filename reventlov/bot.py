from future.utils import iteritems
import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from reventlov.plugins import BotPlugins

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self):
        self.updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('settings', self.settings))
        self.dispatcher.add_handler(CommandHandler(
            'enable_plugin',
            self.enable_plugin,
            pass_args=True,
        ))
        self.plugins = BotPlugins(self.dispatcher)

    @property
    def name(self):
        return self.bot.get_me()['first_name']

    @property
    def username(self):
        return self.bot.get_me()['username']

    @property
    def bot(self):
        return self.updater.bot

    @property
    def dispatcher(self):
        return self.updater.dispatcher

    @property
    def start_message(self):
        msg = f'I am {self.name} (@{self.username})'
        features_msg = ''
        for feature_desc in self.plugins.feature_descs:
            features_msg = f'{features_msg}\n- {feature_desc}'
        msg += features_msg
        return msg

    @property
    def help_message(self):
        msg = 'I am offering the following:'
        msg += f'\n-/start: Greeting and list of features provided.'
        msg += f'\n-/help: Help about my features.'
        msg += f'\n-/settings: View my settings.'
        msg += f'\n-/enable\_plugin: `plugin_name` Enable `plugin_name`'
        for command, message in iteritems(self.plugins.command_descs):
            msg = f'{msg}\n-{command}: {message}'
        return msg

    @property
    def disabled_plugins(self):
        return ', '.join(sorted(self.plugins.disabled_plugins))

    @property
    def enabled_plugins(self):
        return ', '.join(sorted(self.plugins.enabled_plugins))

    def start(self, bot, update):
        '''
        Greeting and list of features I am providing.

        The list of features are including the feature descriptions of all
        the plugins loaded.
        '''
        bot.send_message(
            chat_id=update.message.chat_id,
            text=self.start_message,
            parse_mode=ParseMode.MARKDOWN,
        )

    def help(self, bot, update):
        '''
        Help about my features.

        The list might include many different kinds of help text from all the
        different plugins loaded.
        '''
        bot.send_message(
            chat_id=update.message.chat_id,
            text=self.help_message,
            parse_mode=ParseMode.MARKDOWN,
        )

    def settings(self, bot, update):
        '''
        View my settings.

        These settings can include loaded plugins' settings.
        '''
        msg = 'Here is a list of my settings:'
        msg = f'{msg}\n- `enabled_plugins`: {self.enabled_plugins}'
        msg = f'{msg}\n- `disabled_plugins`: {self.disabled_plugins}'
        bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
        )

    def enable_plugin(self, bot, update, args):
        '''
        Enable a disabled plugin

        Enable one of the disabled plugins.
        '''
        msg = ''
        if len(args) == 1:
            if args[0] in self.disabled_plugins:
                self.plugins.enable(args[0])
                msg = f'Plugin {args[0]} enabled'
            else:
                msg = f'Plugin {args[0]} is not disabled'
        else:
            msg = 'You must specify which plugin you want to enable'
        bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
        )

    def run(self):
        logger.info(f'I am {self.name} (@{self.username})')
        self.updater.start_polling()
