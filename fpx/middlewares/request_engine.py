import httpx
import asyncio

from fpx.utils.errors import RequestError

class RequestEngine:
    def __init__(self, account, client: httpx.AsyncClient):
        self._account = account
        self._client = client
        self.runner = None

    async def execute(self, method: str, url: str, **kwargs):
        attemts = 3
        backoff = 1.5 # множитель времени ожидания
        if method.upper() in ('POST', 'PUT', 'DELETE'):
            if 'data' not in kwargs:
                kwargs['data'] = {}
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self._account._csrf_token is None:
                await self._account.profile.get_user_data()
            if 'csrf_token' not in kwargs['data']:
                kwargs['data']['csrf_token'] = self._account._csrf_token
            if 'X-Cp-Csrf-Token' not in kwargs['headers']:
                kwargs['headers']['X-Cp-Csrf-Token'] = self._account._csrf_token
        for attemt in range(attemts):
            try:
                response = await self._client.request(method, url, **kwargs)
                # флуд контрль
                if response.status_code == 429:
                    sleep_time = int(response.headers.get('Retry-After', 5))
                    if self.runner:
                        for handler in self.runner.handler._handlers['flood']:
                            asyncio.create_task(handler(sleep_time))
                    await asyncio.sleep(sleep_time)
                    return await self.execute(method, url, **kwargs)
                # если чето сервер не ответил
                if response.status_code in (502, 503, 504):
                    sleep_time = backoff ** attemt
                    await asyncio.sleep(sleep_time)
                    continue
                return response
            except httpx.ReadTimeout as e:
                if method.upper() == 'GET':
                    if attemt == attemts - 1: raise e
                    await asyncio.sleep(backoff ** attemt)
                else:
                    raise RequestError(message=f'POST запрос упал по таймауту ответа. Возможно действие выполнилось: {e}')
            except (httpx.ConnectTimeout, httpx.ConnectError) as e:
                if attemt == attemts - 1: raise e
                await asyncio.sleep(backoff ** attemt)
        raise RequestError(message=f"Превышено количество попыток запроса к {url}")