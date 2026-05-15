import asyncio
import httpx
from types import SimpleNamespace

from utils.errors import CriticalRunnerError
from classes.runner.subclasses.chat import ChatRunner
from classes.runner.subclasses.order import OrderRunner
from classes.runner.subclasses.review import ReviewRunner
from classes.runner.subclasses.handler import Handlers

class Runner:
    def __init__(self, account):
        self._account = account
        self._chat = ChatRunner(self)
        self._order = OrderRunner(self)
        self._review = ReviewRunner(self)
        self._handler = Handlers(self)
        self._cache = {
            'msgs': [],
            'old_msgs': [],
            'orders': [],
            'old_orders': [],
            'reviews': [],
            'old_reviews': []
        }
        self._cache_is_updated = False
        self._handlers = {
            'message': [],
            'order': [],
            'confirmed_order': [],
            'new_order': [],
            'refund': [],
            'review': []
        }

    async def idle(self):
        """
        Зацикливает выполнение программы, чтобы фоновые задачи не закрылись.
        """
        while True:
            await asyncio.sleep(3600)
    
    async def _run_loop(self, timer):
        while True:
            try:
                await self._cache_runner()
                await asyncio.sleep(timer)
            except (httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError):
                await asyncio.sleep(timer)
            except Exception as e:
                raise CriticalRunnerError(message=str(e))

    async def runner_polling(self, timer, is_background:bool=False):
        '''
        Запускает поиск новых событий.

        Args:
            timer (str): Задержка в секундах, раз в которую будет происходить обновление кеша (рекомендуемо 3-5 сек).   
            is_background (bool): По дефолту True(в фоне). Определяет, будет ли функция запущена в фоне или нет (если не в фоне, блокирует остальные процессы). 
        '''
        if is_background:
            asyncio.create_task(self._run_loop(timer))
        else:
            await self._run_loop(timer)

    async def _warm_up(self):
        '''Прогрев кеша'''
        for _ in range(2):
            await self._chat._update_chat_cache()
            await self._order._update_order_cache()
            await self._review._update_review_cache()
        self._cache_is_updated = True

    async def _cache_runner(self):
        '''Управляет кешем'''
        if not self._cache_is_updated:
            await self._warm_up()
            return
        await self._chat._check_chats()
        await self._order._check_orders()
        await self._review._check_reviews()