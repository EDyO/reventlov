import logging

from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)

class Bot(object):
    def __init__(self, dispatcher):
        dispatcher.add_handler(CommandHandler(
            'set',
            self.set_timer,
            pass_args=True,
            pass_job_queue=True,
            pass_chat_data=True,
        ))
        dispatcher.add_handler(CommandHandler(
            'unset',
            self.unset_timer,
            pass_chat_data=True,
        ))
        self.version = '0.0.1'
        logger.info("Pomodoro plugin v{} loaded".format(self.version))

    @property
    def feature_desc(self):
        return "I can manage pomodoro alarms for you"

    def alarm(self, bot, job):
        bot.send_message(job.context['chat_id'], text=job.context['text'])

    def set_timer(self, bot, update, args, job_queue, chat_data):
        chat_id = update.message.chat_id
        try:
            due = int(args[0])
            if due < 0:
                update.message.reply_text(
                    'Sorry we can not go back to future!'
                )
                return
            job = job_queue.run_once(self.alarm, due, context={
                'chat_id': chat_id,
                'text': ' '.join(args[1:]) or 'Beep!'
            })
            chat_data['job'] = job
            update.message.reply_text('Timer successfully set!')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <seconds> <message...>')

    def unset_timer(self, bot, update, chat_data):
        if 'job' not in chat_data:
            update.message.reply_text('You have no active timer')
            return

        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']

        update.message.reply_text('Timer successfully unset!')
