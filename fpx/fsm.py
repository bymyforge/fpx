


class BaseStorage:
    async def set_state(self, chat_id: str, state: str | None):
        '''Задаёт стейт'''
        pass

    async def get_state(self, chat_id: str) -> str | None:
        '''Находит состояние'''
        pass
    
    async def update_data(self, chat_id: str, data_key: str, data_value: str) -> None:
        '''Обновляет данные состояния'''
        pass

    async def get_data(self, chat_id: str):
        '''Забирает данные состояния'''
        pass

    async def clear_state(self, chat_id: str):
        '''Очищает состояние'''
        pass

class MemoryStorage(BaseStorage):
    def __init__(self):
        self._states = {}

    def _init_chat(self, chat_id: str):
        if chat_id not in self._states:
            self._states[chat_id] = {'state': None, 'data': {}}

    async def set_state(self, chat_id: str, state: str | None):
        self._init_chat(chat_id)
        self._states[chat_id]['state'] = state

    async def get_state(self, chat_id: str) -> str | None:
        if chat_id not in self._states:
            return None
        return self._states[chat_id]['state']
    
    async def update_data(self, chat_id: str, data_key: str, data_value: str) -> None:
        self._init_chat(chat_id)
        self._states[chat_id]['data'].update({data_key: data_value})

    async def get_data(self, chat_id: str):
        if chat_id not in self._states:
            return {}
        return self._states[chat_id]['data']

    async def clear_state(self, chat_id: str):
        self._states.pop(chat_id, None)