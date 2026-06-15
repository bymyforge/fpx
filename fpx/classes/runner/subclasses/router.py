
import asyncio
import inspect
from typing import Awaitable, Callable

from fpx.fsm import FSMContext
from fpx.models.chat import Message
from fpx.utils.dependencies import Dependency


class Router:
    def __init__(self):
        self._handlers = {
            'message': [],
            'order': [],
            'confirmed_order': [],
            'new_order': [],
            'refund': [],
            'review': [],
            'lot_category': [],
            'chip_category': [],
            'commands': [],
            'error': [],
            'order_command': [],

            # системные
            'startup': [],
            'flood': []
        }
        self._middlewares = []

    def middleware(self):
        '''Декоратор регистрации мидлваря'''
        def decorator(func):
            self._middlewares.append(func)
            return func
        return decorator

    async def invoke(self, h_func, event, state_ctx=None, args=None):
        '''Вызывает хендлер'''
        async def endpoint(ev):
            sig = inspect.signature(h_func)
            kwargs = {}
            arg_index = 0
            for param_name, param in sig.parameters.items():
                if param.annotation is type(ev):
                    kwargs[param_name] = ev
                    continue
                if state_ctx and param.annotation == FSMContext:
                    kwargs[param_name] = state_ctx
                    continue
                if isinstance(param.default, Dependency):
                    dep_func = param.default.dependency
                    if asyncio.iscoroutinefunction(dep_func):
                        kwargs[param_name] = await dep_func(ev)
                    else:
                        kwargs[param_name] = dep_func(ev)
                if args and param.default is inspect.Parameter.empty:
                    if arg_index < len(args):
                        kwargs[param_name] = args[arg_index]
                        arg_index += 1
            await h_func(**kwargs)
        call_next = endpoint
        for mw in reversed(self._middlewares):
            async def make_next(mw=mw, next_=call_next):
                async def call(ev):
                    return await mw(ev, next_)
                return call
            call_next = await make_next()
        await call_next(event)

    def include_router(self, router):
        '''Метод для подключения плагинов и сторонних роутеров'''
        for event_type, funcs in router._handlers.items():
            if event_type in self._handlers:
                self._handlers[event_type].extend(funcs)

    def order_targets(self, target_dict: dict):
        '''
        Метод для регистрации команд автоматизации новых заказов.

        Args:
            target_dict (dict): Словарь вида {'target': answer_new_def, 'моя пометка в описании': another_func}
        '''
        self._handlers['order_command'].append({
            'trigger_command': target_dict
        })

    def message_commands(self, command_dict: dict):
        '''
        Метод для регистрации команд автоматизации сообщений.

        Args:
            target_dict (dict): Словарь вида {'command': answer_new_def, '!start': another_func}
        '''
        self._handlers['commands'].append({
            'command': command_dict
        })

    def on_error(self):
        '''Декоратор для отлова ошибок'''
        def decorator(func):
            self._handlers['error'].append(func)
            return func
        return decorator

    def on_message(
        self,
        text: str | None = None,
        contains: str | list[str] | None = None,
        regex: str | list[str] | None = None,
        custom: Callable[['Message'], bool | Awaitable[bool]] | None = None,
        mapping: dict[str, str] | None = None,
        state: str | None = None,
        ignore_chat_id: str | int | list[str | int] | None = None,
        ignore_sender: str | list[str] | None = None,
        priority: int = 0
    ):
        r'''Декоратор отслеживает новые сообщения.
        Важно что если сделать несколько хендлеров с одинаковыми фильтрами, то подходящее
        сообщение будет вызвано только под первый хендлер.

        Args:
            - text (str | None): Срабатывает, если сообщение НАЧИНАЕТСЯ с этого текста.
            - contains (str | list | None): Срабатывает, если в сообщении
                есть эти ключевые слова (можно строку или список слов).
            - regex (str | list | None): Фильтр по регуляркам (re.search).
                Ест сырые строки типа r'^id\d+$' или список паттернов.
            - custom (Callable | None): Твоя кастомная проверка.
                Сюда можно закинуть лямбду или синхронную/асинхронную функцию, которая возвращает True/False.
            - mapping (dict | None): Умный автоответчик.
                Передаешь словарь {'триггер': 'ответ'}, и скрипт сам ответит за тебя, подставив переменные.
            - state (str | None): Фильтр по состоянию FSM.
                Хендлер сработает только если текущий стейт чата совпадает с этим.
            - ignore_chat_id (str | int | list | None): Черный список для чатов.
                Айдишники отсюда скрипт будет просто игнорить (одиночный ID или список).
            - ignore_sender (str | list | None): Черный список для юзеров. Скрипт проигнорит сообщения от них.
            - priority (int | None): Приоритет декоратора, чем выше тем раньше проверяется (12 проверит раньше чем 11)

        Returns:
            Message: Объект, содержащий:
                - sender (str): Имя отправителя
                - chat_id (str): Айди чата (node id)
                - text (str): Сообщение, которое было отправлено в этом чате
                - is_system (bool): Системное ли сообщение
                - answer (method): При указании текста в аргументах, отвечает на сообщение
        '''
        def decorator(func):
            self._handlers['message'].append({
                'function': func,
                'filter_text': text,
                'contains': contains,
                'regex': regex,
                'custom': custom,
                'mapping': mapping,
                'state': state,
                'ignore_chat_id': ignore_chat_id,
                'ignore_sender': ignore_sender,
                'priority': priority
            })
            self._handlers['message'].sort(key=lambda h: h['priority'], reverse=True)
            return func
        return decorator

    def on_orders(self, mapping: list[str] | None = None):
        '''
        Декоратор отслеживает все события заказов.
        Не рекомендуется использовать вместе с on_cofirmed_orders, on_new_order, on_refunded_orders
        во избежание дублирования событий.

        Returns:
            Order: Объект, содержащий:
                - order_id (str): Уникальный ID заказа
                - description (str): Описание лота
                - order_time (str): Время оплаты заказа
                - client_name (str): Имя клиента
                - price (str): Цена товара
                - status (str): Статус заказа
                - name (str): Название товара
                - answer (method): При указании текста в аргументах, отвечает на сообщение
        '''
        if isinstance(mapping, str):
            mapping = [mapping]
        def decorator(func):
            self._handlers['order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_confirmed_orders(self, mapping: list | None = None):
        '''
        Декоратор, который отслеживает только событие подтверждёния заказа.

        Returns:
            Order: Объект, содержащий:
                - order_id (str): Уникальный ID заказа
                - order_time (str): Время оплаты заказа
                - client_name (str): Имя клиента
                - price (str): Цена товара
                - status (str): Статус заказа
                - name (str): Название товара
                - answer (method): При указании текста в аргументах, отвечает на сообщение
        '''
        mapping = [mapping] if isinstance(mapping, str) else mapping
        def decorator(func):
            self._handlers['confirmed_order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_new_order(
        self,
        mapping: list | None = None
    ):
        '''
        Декоратор, который отслеживает только новые заказы.

        Returns:
            Order: Объект, содержащий:
                - order_id (str): Уникальный ID заказа
                - order_time (str): Время оплаты заказа
                - client_name (str): Имя клиента
                - price (str): Цена товара
                - status (str): Статус заказа
                - name (str): Название товара
                - answer (method): При указании текста в аргументах, отвечает на сообщение
        '''
        mapping = [mapping] if isinstance(mapping, str) else mapping
        def decorator(func):
            self._handlers['new_order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_new_review(self, stars: int | None = None):
        '''Декоратор отслеживает новые отзывы.

        Args:
            - stars (int | None): Количество звёзд, на которое хендлер будет реагировать (не обязательно передавать).

        Returns:
            CurReview: Объект, содержащий:
                - text (str): Текст отзыва
                - stars (int): Кол-во звёзд, оставленных под отзывом
                - author (str): Автор отзыва
                - item_name (str): Заказ, под которым оставлен отзыв
        '''
        def decorator(func):
            self._handlers['review'].append({
                'function': func,
                'stars': stars
            })
            return func
        return decorator

    def on_refunded_orders(self, mapping: list | None = None):
        '''
        Декоратор отслеживает события возврата заказов.

        Returns:
            Order: Объект, содержащий:
                - order_id (str): Уникальный ID заказа
                - order_time (str): Время оплаты заказа
                - client_name (str): Имя клиента
                - price (str): Цена товара
                - status (str): Статус заказа
                - name (str): Название товара
                - answer (method): При указании текста в аргументах, отвечает на сообщение
        '''
        mapping = [mapping] if isinstance(mapping, str) else mapping
        def decorator(func):
            self._handlers['refund'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_lot_category(self):
        '''
        Декоратор отслеживает снижение цен на лоты.

        Returns:
            CategoryLastLot: Объект, содержащий:
                - price (float): Цена лота
                - offer_id (str): Айди лота
        '''
        def decorator(func):
            self._handlers['lot_category'].append(func)
            return func
        return decorator

    def on_chip_category(self):
        '''
        Декоратор отслеживает снижение цен на чипсах(коротких лотов под валюты).

        Returns:
            CategoryLastLot: Объект, содержащий:
                - price (float): Цена лота
                - offer_id (str): Айди лота
        '''
        def decorator(func):
            self._handlers['chip_category'].append(func)
            return func
        return decorator

    def on_startup(self):
        '''Декоратор отслеживает запуск раннера'''
        def decorator(func):
            self._handlers['startup'].append(func)
            return func
        return decorator

    def on_flood(self):
        '''Декоратор отслеживает флуд в системе'''
        def decorator(func):
            self._handlers['flood'].append(func)
            return func
        return decorator
