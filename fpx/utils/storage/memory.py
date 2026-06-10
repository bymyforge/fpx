from .base import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self):
        self._states = {}

    def _init_chat(self, chat_id: str):
        if chat_id not in self._states:
            self._states[chat_id] = {'state': None, 'data': {}}

    async def set_state(self, chat_id: str | int, state: str | None):
        chat_id = str(chat_id)
        self._init_chat(chat_id)
        self._states[chat_id]['state'] = state

    async def get_state(self, chat_id: str | int) -> str | None:
        return self._states.get(str(chat_id), {}).get('state')
    
    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        chat_id = str(chat_id)
        self._init_chat(chat_id)
        self._states[chat_id]['data'].update(kwargs)

    async def get_data(self, chat_id: str | int) -> dict:
        return self._states.get(str(chat_id), {}).get('data', {})

    async def clear_state(self, chat_id: str | int):
        self._states.pop(str(chat_id), None)