import os
import logging

from telegram.ext import Updater, CommandHandler

from reventlov.plugins import get_plugins

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self):
        self.updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.plugins = get_plugins(self.dispatcher)

    @property
    def name(self):
        return self.bot.get_me()["first_name"]

    @property
    def username(self):
        return self.bot.get_me()["username"]

    @property
    def bot(self):
        return self.updater.bot

    @property
    def dispatcher(self):
        return self.updater.dispatcher

    @property
    def start_message(self):
        msg = "I am {} (@{})".format(self.name, self.username)
        for plugin in self.plugins:
            msg = "{}\n{}".format(msg, self.plugins[plugin].feature_desc)
        return msg

    def start(self, bot, update):
        bot.send_message(
            chat_id=update.message.chat_id,
            text=self.start_message,
        )

    def help(self, bot, update):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="This is my help",
        )

    def run(self):
        logger.info("I am {} (@{})".format(self.name, self.username))
        self.updater.start_polling()
