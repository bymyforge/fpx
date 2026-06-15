from ._chats import ChatParser
from ._lots import LotParser
from ._orders import OrderParser
from ._profile import ProfileParser


class FpxParser(ChatParser, LotParser, OrderParser, ProfileParser):
    '''
    Главный парсер fpx
    Собирает внутри себя методы из отдельных модулей.
    '''
    pass
