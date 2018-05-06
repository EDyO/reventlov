import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from reventlov.plugins import get_plugins

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self):
        self.updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('settings', self.settings))
        self.plugins = get_plugins(self.dispatcher)

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
        msg = 'I am {} (@{})'.format(self.name, self.username)
        features_msg = ''
        for plugin in self.plugins:
            features_msg = '{}\n- {}'.format(
                features_msg,
                self.plugins[plugin].feature_desc,
            )
        if len(features_msg) > 0:
            msg = '{}{}'.format(msg, features_msg)
        return msg

    @property
    def help_message(self):
        msg = 'I am offering the following:'
        for handler in self.dispatcher.handlers[0]:
            if handler.__class__ == CommandHandler:
                help_msg = handler.callback.__doc__ or '\nUndefined command'
                handler_msg = '- /{}: {}'.format(
                    handler.command[0],
                    help_msg.splitlines()[1].strip()
                )
            else:
                handler_msg = 'Undefined message'
            msg = '{}\n{}'.format(msg, handler_msg)
        return msg.replace('_', '\_')

    @property
    def loaded_plugins(self):
        return ','.join([name.split('.')[-1] for name in self.plugins.keys()])

    @property
    def settings_message(self):
        msg = 'Here is a list of my settings:'
        msg = '{}\n- `loaded_plugins`: {}'.format(msg, self.loaded_plugins)
        return msg

    def start(self, bot, update):
        '''
        Greet and list of features I am providing.

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
        List my settings.

        These settings can include loaded plugins' settings.
        '''
        bot.send_message(
            chat_id=update.message.chat_id,
            text=self.settings_message,
            parse_mode=ParseMode.MARKDOWN,
        )

    def run(self):
        logger.info('I am {} (@{})'.format(self.name, self.username))
        self.updater.start_polling()
