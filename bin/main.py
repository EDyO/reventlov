#!/usr/bin/env python
from reventlov.bot import Bot
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

if __name__ == '__main__':
    bot = Bot()
    bot.run()
