import asyncio
from typing import Any

import httpx

from fpx.classes.runner.subclasses._category import CategoryRunner
from fpx.classes.runner.subclasses._chat import ChatRunner
from fpx.classes.runner.subclasses._order import OrderRunner
from fpx.classes.runner.subclasses._review import ReviewRunner
from fpx.classes.runner.subclasses.router import Router
from fpx.utils import errors as fpx_err


class Runner:
    def __init__(self, account):
        self._account = account
        self._chat = ChatRunner(self)
        self._order = OrderRunner(self)
        self._review = ReviewRunner(self)
        self._category = CategoryRunner(self)
        self.router = Router()
        self.storage = None
        self._cache = {
            'msgs': [],
            'old_msgs': [],
            'orders': [],
            'old_orders': [],
            'reviews': [],
            'old_reviews': [],
            'lot_categories': [],
            'old_lot_categories': [],
            'chip_categories': [],
            'old_chip_categories': []
        }
        self._cache_is_updated = False

    async def idle(self):
        """
        Зацикливает выполнение программы, чтобы фоновые задачи не закрылись.
        Если не использовать, код не будет работать.
        """
        while True:
            await asyncio.sleep(3600)

    async def _run_loop(
        self,
        timer,
        watch_lots: list[str | int] | None = None,
        watch_chips: list[str | int] | None = None
    ):
        while True:
            try:
                await self._cache_runner(watch_lots, watch_chips)
                await asyncio.sleep(timer)
            except fpx_err.FpxRequestError:
                await asyncio.sleep(60)
            except fpx_err.FpxAccountError:
                await asyncio.sleep(5)
                continue
            except (httpx.HTTPError, httpx.NetworkError):
                await asyncio.sleep(timer)
            except Exception as e:
                raise fpx_err.FpxCriticalRunnerError(message=str(e))

    async def start_polling(
        self,
        timer=3,
        is_background: bool=True,
        watch_lots: list[str | int] | None = None,
        watch_chips: list[str | int] | None = None
    ):
        '''
        Запускает поиск новых событий.

        Args:
            timer (str): Задержка в секундах, раз в которую будет происходить обновление кеша (рекомендуемо 3-5 сек).
            is_background (bool): По дефолту True(в фоне).
                Определяет, будет ли функция запущена в фоне
                или нет (если не в фоне, блокирует остальные процессы).
            watch_lots (list): Можно не передавать.
                Список категорий лотов, которые будет проверять скрипт.
            watch_chips (list): Можно не передавать.
                Список категорий чипсов(коротких лотов под валюты),
                которые будет проверять скрипт.
        '''
        if is_background:
            task = asyncio.create_task(self._run_loop(timer, watch_lots, watch_chips))
            return task
        else:
            await self._run_loop(timer, watch_lots, watch_chips)

    async def _warm_up(self, watch_lots, watch_chips):
        '''Прогрев кеша'''
        await self._account.profile.get_user_data()
        tasks = []
        if watch_lots is not None:
            tasks.append(self._category._check_lot_categories(watch_lots))
        if watch_chips is not None:
            tasks.append(self._category._check_chip_categories(watch_chips))
        tasks.extend([
            self._chat._update_chat_cache(),
            self._order._update_order_cache(),
            self._review._update_review_cache()
        ])
        results = await asyncio.gather(*tasks, return_exceptions=True)
        is_good = True
        for result in results:
            if isinstance(result, Exception):
                await self._handle_error(None, result)
                is_good = False
        if is_good:
            self._cache_is_updated = True
            for handler in self.router._handlers['startup']:
                try:
                    await handler()
                except Exception as e:
                    await self._handle_error(None, e)
        else:
            self._cache_is_updated = False

    async def _cache_runner(self, watch_lots, watch_chips):
        '''Управляет кешем'''
        if not self._cache_is_updated:
            await self._warm_up(watch_lots, watch_chips)
            return
        tasks = []
        if watch_lots is not None:
            tasks.append(self._category._check_lot_categories(watch_lots))
        if watch_chips is not None:
            tasks.append(self._category._check_chip_categories(watch_chips))
        tasks.extend([
            self._chat._check_chats(),
            self._order._check_orders(),
            self._review._check_reviews()
        ])
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                await self._handle_error(None, result)

    async def _handle_error(self, event: Any, exception: Exception):
        '''Централизованная обработка любых ошибок.
        event может быть Message, Order, Review или None.
        Советую проверять через if isinstanse(exception, fpx_err...)
        '''
        error_handlers = self.router._handlers.get('error', [])
        for handler in error_handlers:
            if handler:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event, exception)
                else:
                    handler(event, exception)
