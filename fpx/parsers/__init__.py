from .chats import ChatParser
from .lots import LotParser
from .orders import OrderParser
from .profile import ProfileParser

class FpxParser(ChatParser, LotParser, OrderParser, ProfileParser):
    '''
    Главный парсер fpx
    Собирает внутри себя методы из отдельных модулей.
    '''
    pass