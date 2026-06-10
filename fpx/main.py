import httpx

from fpx.classes.account.account import Account
from fpx.classes.runner.runner import Runner
from fpx.fsm import MemoryStorage, BaseStorage, FileStorage, RedisStorage

class FunPayTools:
    def __init__(self, gkey, storage: BaseStorage | FileStorage | RedisStorage | None = None, proxy = None, http_client = None):
        self._cookies = {
            'golden_key': gkey,
            'locale': 'ru'
        }
        self._headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept-Language": "ru-RU,ru;q=0.9"
        }
        mounts = {}
        if proxy:
            mounts = {
                "http://": httpx.AsyncHTTPTransport(proxy=proxy),
                "https://": httpx.AsyncHTTPTransport(proxy=proxy),
            }
        if http_client:
            self._client = http_client
            self._client.cookies.update(self._cookies)
            self._client.headers.update(self._headers)
        else:
            self._client = httpx.AsyncClient(
                http2=True,
                cookies=self._cookies,
                headers=self._headers,
                base_url='https://funpay.com',
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                timeout=httpx.Timeout(15.0),
                mounts=mounts
            )
        self.account = Account(self._client)
        self.runner = Runner(self.account)
        self.router = self.runner.router
        self.account._request_engine.runner = self.runner
        self.storage = storage or MemoryStorage()
        self.runner.storage = self.storage

    async def _close(self):
        await self._client.aclose()

    async def __aenter__(self): 
        return self

    async def __aexit__(self, *exc): 
        await self._close()