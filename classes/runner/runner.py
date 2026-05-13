import asyncio
import httpx
from types import SimpleNamespace

from classes.runner.subclasses.chat import ChatRunner

class Runner:
    def __init__(self, account):
        self.account = account
        self.chat = ChatRunner(self)
        self.msgs = []
        self.orders = []
        self.old_msgs = []
        self.old_orders = []

    async def cache_runner(self):
        await self.chat.update_chat_cache()
        chats = await self.chat.compare_chat_cache()
        if chats:
            print(chats)

    async def runner_polling(self, timer):
        '''
        Принимает timer - количество секунд, раз в который будет проверка новых событий
        Запускает цикл раннера(поиск событий), раннер сравнивает старый кеш с новым в timer секунд, рекомендуемая задержка 3-5 сек
        '''
        while True:
            try:
                await self.cache_runner()
                await asyncio.sleep(timer)
            except httpx.ConnectTimeout:
                await asyncio.sleep(timer)
        # добавить декораторы, чтоб юзер мог удобно ловить события, но для начала реализовать выборку нужного события(типа новое сообщение, новый заказ и тд.)