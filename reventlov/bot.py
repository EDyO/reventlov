import os
import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from reventlov.plugins import get_plugins, add_plugin

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
        msg = f'I am {self.name} (@{self.username})'
        features_msg = ''
        for plugin in self.plugins:
            feature_desc = self.plugins[plugin].feature_desc
            features_msg = f'{features_msg}\n- {feature_desc}'
        if len(features_msg) > 0:
            msg = f'{msg}{features_msg}'
        return msg

    @property
    def help_message(self):
        msg = 'I am offering the following:'
        for handler in self.dispatcher.handlers[0]:
            if handler.__class__ == CommandHandler:
                help_msg = handler.callback.__doc__ or '\nUndefined command'
                help_header = help_msg.splitlines()[1].strip()
                cmd = handler.command[0]
                handler_msg = f'- /{cmd}: {help_header}'
            else:
                handler_msg = 'Undefined message'
            msg = f'{msg}\n{handler_msg}'
        msg = msg.replace('_', '\_')
        return msg

    @property
    def disabled_plugins(self):
        return ', '.join(sorted(
            [name for name in self.plugins if self.plugins[name] is None]
        ))

    @property
    def enabled_plugins(self):
        return ', '.join(sorted(
            [name for name in self.plugins if self.plugins[name]]
        ))

    @property
    def settings_message(self):
        msg = 'Here is a list of my settings:'
        msg = f'{msg}\n- `enabled_plugins`: {self.enabled_plugins}'
        msg = f'{msg}\n- `disabled_plugins`: {self.disabled_plugins}'
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

    def enable_plugin(self, bot, update, args):
        '''
        Enable currently disabled plugin.
        '''
        if len(args) > 0:
            if args[0] in self.disabled_plugins:
                self.plugins = add_plugin(args[0], self.dispatcher)
            else:
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f'Plugin {args[0]} is not disabled',
                )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text='You must specify the plugin name',
            )

    def run(self):
        logger.info(f'I am {self.name} (@{self.username})')
        self.updater.start_polling()
