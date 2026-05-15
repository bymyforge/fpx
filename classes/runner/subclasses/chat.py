


class ChatRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _compare_chat_cache(self):
        '''
        Сравнивает старый кеш сообщений с новым, если находит отличия, выносит сообщение в список, после чего возвращает полный список
        '''
        result = []
        if self.runner._cache['msgs'] != self.runner._cache['old_msgs']:
            for message in self.runner._cache['msgs']:
                if message not in self.runner._cache['old_msgs']:
                    stop_words = ('оплатил заказ', 'можете перейти в discord', 'написал отзыв', 'изменил отзыв', 'вернул деньги', 'подтвердил успешное выполнение')
                    msg_lower = message['last_msg'].lower()
                    if not any(word in msg_lower for word in stop_words):
                        result.append(message)
        return result

    async def _update_chat_cache(self):
        '''
        Обновляет кеш последних чатов
        '''
        chats = await self.runner._account.chat.get_chats()
        result = []
        counter = 0
        for chat in chats:
            if counter > 30:
                break
            chat = {'sender': chat.username, 'id': chat.id, 'last_msg': chat.last_msg}
            result.append(chat)
            counter += 1
        self.runner._cache['old_msgs'] = self.runner._cache['msgs']
        self.runner._cache['msgs'] = result

    async def _check_chats(self):
        await self.runner._chat._update_chat_cache()
        chats = await self.runner._chat._compare_chat_cache()
        if chats:
            for handler in self.runner._handlers['message']:
                await handler(chats)