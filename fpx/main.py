import httpx

from fpx.classes.account.account import Account
from fpx.classes.runner.runner import Runner

class FunPayTools:
    def __init__(self, gkey):
        self.cookies = {'golden_key': gkey}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept-Language": "ru-RU,ru;q=0.9"
        }
        self.client = httpx.AsyncClient(
            http2=True,
            cookies=self.cookies,
            headers=self.headers,
            base_url='https://funpay.com'
        )
        self.account = Account(self.client)
        self.runner = Runner(self.account)
        self.handler = self.runner.handler
        self.account._request_engine.runner = self.runner