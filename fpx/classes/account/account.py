
from dataclasses import dataclass, field
from typing import Optional

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
from fpx.middlewares._request_engine import RequestEngine

@dataclass
class AccountData:
    '''Хранит данные аккаунта'''
    username: Optional[str] = None
    user_id: Optional[str] = None
    _csrf_token: Optional[str] = None
    _node_names: dict = field(default_factory=dict)

class Account:
    '''
    Взаимодействует с аккаунтом.
    '''
    def __init__(self, client):
        self._http_client = client
        self._client = FunPayClient(self, self._http_client)
        self._request_engine = RequestEngine(self, self._http_client)
        self._parser = FpxParser()
        self.data = AccountData()
        self.chat = ChatManager(self)
        self.addons = AddonsManager(self)
        self.profile = ProfileManager(self)
        self.order = OrderManager(self)
        self.lot = LotManager(self)
        self.editor = FunPayEditor(self)
        self.review = ReviewManager(self)
        self.category = CategoryManager(self)