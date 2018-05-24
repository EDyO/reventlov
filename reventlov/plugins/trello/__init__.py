import os
import logging

from telegram import ParseMode
from telegram.ext import CommandHandler
from trello import TrelloClient

from reventlov.bot_plugins import get_list_from_environment
from reventlov.bot_plugin import BotPlugin

version = '0.0.1'
logger = logging.getLogger(__name__)
logger.info(f'Trello module v{version} loaded')


class TrelloPlugin(BotPlugin):
    '''
    I can manage Trello boards for you
    '''
    def __init__(self, dispatcher):
        self.client = TrelloClient(
            api_key=os.getenv('TRELLO_API_KEY'),
            api_secret=os.getenv('TRELLO_API_SECRET'),
            token=os.getenv('TRELLO_API_TOKEN'),
        )
        self.admins = get_list_from_environment('TRELLO_ADMINS')
        self.load_orgs()
        self.__boards = []
        self.handlers = [
            CommandHandler(
                'list',
                self.list_objects,
                pass_args=True,
            )
        ]
        self.add_handlers(dispatcher)
        self.version = '0.0.1'
        logger.info(f'Trello plugin v{version} enabled')

    @property
    def organization(self):
        if len(self.__orgs) == 1:
            return self.__orgs[0]
        else:
            return os.getenv('TRELLO_DEFAULT_ORGANIZATION')

    def load_orgs(self):
        logger.info('Getting organizations')
        self.__orgs = self.client.list_organizations()

    def load_boards(self):
        logger.info('Getting boards')
        self.__boards = self.organization.get_boards('open')

    @property
    def orgs(self):
        if len(self.__orgs) == 0:
            self.load_orgs()
        return self.__orgs

    @property
    def boards(self):
        if len(self.__boards) == 0:
            self.load_boards()
        return self.__boards

    @property
    def org_names(self):
        return [org.name for org in self.orgs]

    @property
    def board_names(self):
        return [board.name for board in self.boards]

    def get_board(self, board_name):
        board_found = None
        for board in self.boards:
            if board.name == board_name:
                board_found = board
                break
        return board_found

    def list_orgs(self):
        msg = '\n'.join([
            f'- *{org_name}*' if org_name == self.organization.name
            else f'- {org_name}'
            for org_name in self.org_names
        ])
        return msg, ParseMode.MARKDOWN

    def list_boards(self):
        msg = '\n'.join([
            f'- {board_name}'
            for board_name in self.board_names
        ])
        return msg, ParseMode.MARKDOWN

    def list_column_cards(self, column):
        msg = '\n'.join([
            f'    + {card.name}'
            for card in column.list_cards()
        ])
        return msg

    def list_board_columns(self, board_name):
        msg = f'No such board `{board_name}`'
        board = self.get_board(board_name)
        if board is not None:
            msg = '\n'.join([
                f'- {column.name} ({column.cardsCnt()} cards) '
                f'\n{self.list_column_cards(column)}'.strip()
                for column in board.open_lists()
            ])
        return msg, ParseMode.HTML

    def list_objects(self, bot, update, args):
        '''
        List Trello objects visible to me.

        Object type depends on first argument:
          - `orgs`: List organizations.
          - `boards`: List boards.
          - `board_name`: List cards in `board_name`.
        By default it lists organizations.
        '''
        msg = ''
        parse_mode = None
        if update.message.from_user.username in self.admins:
            if len(args) < 1 or args[0] == 'orgs':
                msg, parse_mode = self.list_orgs()
            elif args[0] == 'boards':
                msg, parse_mode = self.list_boards()
            elif args[0] in self.board_names:
                msg, parse_mode = self.list_board_columns(args[0])
            else:
                msg = f'No such board `{args[0]}`'
                parse_mode = ParseMode.MARKDOWN
            msg += '\n\nYou can specify either one of: `orgs`, `boards`, ' \
                   'or use a `board_name` to list its cards'
        else:
            msg = 'You must be admin to list Trello objects'
        bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
            parse_mode=parse_mode,
        )
