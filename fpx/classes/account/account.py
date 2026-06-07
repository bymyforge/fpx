
from fpx._api._client import FunPayClient
from fpx._parsers import FpxParser
from fpx.classes.account.subclasses.chat import ChatManager
from fpx.classes.account.subclasses.addons import AddonsManager
from fpx.classes.account.subclasses.profile import ProfileManager
from fpx.classes.account.subclasses.order import OrderManager
from fpx.classes.account.subclasses.lot import LotManager
from fpx.classes.account.subclasses.editor import FunPayEditor
from fpx.classes.account.subclasses.review import ReviewManager
from fpx.classes.account.subclasses.category import CategoryManager
from fpx.middlewares.request_engine import RequestEngine

class Account:
    '''
    Взаимодействует с аккаунтом.
    '''
    def __init__(self, client):
        self.http_client = client
        self.client = FunPayClient(self, self.http_client)
        self._request_engine = RequestEngine(self, self.http_client)
        self._parser = FpxParser()
        self.username = None
        self.user_id = None
        self._csrf_token = None
        self._node_names = {}
        self.chat = ChatManager(self)
        self.addons = AddonsManager(self)
        self.profile = ProfileManager(self)
        self.order = OrderManager(self)
        self.lot = LotManager(self)
        self.editor = FunPayEditor(self)
        self.review = ReviewManager(self)
        self.category = CategoryManager(self)