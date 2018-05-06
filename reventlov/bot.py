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
    def username(self):
        return self.bot.get_me()["username"]

    @property
    def bot(self):
        return self.updater.bot

    @property
    def dispatcher(self):
        return self.updater.dispatcher

    def start(self, bot, update):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm {}, please talk to me".format(self.username),
        )

    def help(self, bot, update):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="This is my help",
        )

    def run(self):
        logger.info("I am {}".format(self.username))
        self.updater.start_polling()
