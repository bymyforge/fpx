from fpx.models.chat import Message


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
                        result.append(Message(sender=message['sender'], chat_id=message['chat_id'], text=message['last_msg'], is_system=False))
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
            chat = {'sender': chat.username, 'chat_id': chat.id, 'last_msg': chat.last_msg}
            result.append(chat)
            counter += 1
        self.runner._cache['old_msgs'] = self.runner._cache['msgs']
        self.runner._cache['msgs'] = result

    async def _trigger_message_handlers(self, message):
        if self.runner._account.username == message.sender:
            return
        msg_text = message.text.lower()
        for handler in self.runner.handler._handlers['message']:
            if handler['mapping'] is not None:
                matched = False
                for trigger, reply in handler['mapping'].items():
                    if msg_text.startswith(trigger.lower()):
                        formatted_reply = reply.format(
                            sender=message.sender,
                            chat_id=message.chat_id,
                            text=message.text
                        )
                        await message.answer(formatted_reply)
                        matched = True
                        break
                if matched:
                    await handler['function'](message)
                    continue
            filter_text = handler['filter_text']
            if filter_text is None and handler['mapping'] is None:
                await handler['function'](message)
                continue
            if isinstance(filter_text, str) and msg_text.startswith(filter_text.lower()):
                await handler['function'](message)
                continue

    async def _check_chats(self):
        await self.runner._chat._update_chat_cache()
        chats = await self.runner._chat._compare_chat_cache()
        if chats:
            for chat in chats:
                msg_obj = await self.runner._account.chat.get_chat_data(chat.chat_id)
                message = msg_obj.last_message
                chat = Message(sender=message['sender'], chat_id=chat.chat_id, text=chat.text, is_system=message['is_system'])   
                chat._client = self.runner
                await self._trigger_message_handlers(chat)