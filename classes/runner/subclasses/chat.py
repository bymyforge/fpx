


class ChatRunner:
    def __init__(self, runner):
        self.runner = runner

    async def compare_chat_cache(self):
        '''
        Сравнивает старый кеш сообщений с новым, если находит отличия, выносит сообщение в список, после чего возвращает полный список
        '''
        result = []
        if self.runner.msgs != self.runner.old_msgs:
            for message in self.runner.msgs:
                if message not in self.runner.old_msgs:
                    result.append(message)
        return result

    async def update_chat_cache(self):
        '''
        Обновляет кеш последних чатов
        '''
        chats = await self.runner.account.chat.get_chats()
        result = []
        counter = 0
        for chat in chats:
            if counter > 30:
                break
            chat = {'sender': chat.username, 'id': chat.id, 'last_msg': chat.last_msg}
            result.append(chat)
            counter += 1
        self.runner.old_msgs = self.runner.msgs
        self.runner.msgs = result