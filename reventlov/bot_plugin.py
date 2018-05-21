from telegram.ext import CommandHandler


class BotPlugin(object):
    @property
    def commands(self):
        return [
            handler
            for handler in self.handlers
            if handler.__class__ == CommandHandler
        ]

    def add_handlers(self, dispatcher):
        for handler in self.handlers:
            dispatcher.add_handler(handler)

    def remove_handlers(self, dispatcher):
        for handler in self.handlers:
            dispatcher.remove_handler(handler)
