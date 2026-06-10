import json
import asyncio
import os


class BaseStorage:
    async def set_state(self, chat_id: str | int, state: str | None) -> None:
        '''Задаёт стейт'''
        pass

    async def get_state(self, chat_id: str | int) -> str | None:
        '''Находит состояние'''
        pass
    
    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        '''Обновляет данные состояния (принимает kwargs)'''
        pass

    async def get_data(self, chat_id: str | int) -> dict:
        '''Забирает данные состояния'''
        pass

    async def clear_state(self, chat_id: str | int) -> None:
        '''Очищает состояние и данные полностью'''
        pass


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


class FileStorage(BaseStorage):
    def __init__(self, file_path: str):
        self._states = {}
        self.file_path = file_path
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._states = json.load(f)
            except json.JSONDecodeError:
                self._states = {}
    
    def _write_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self._states, f, ensure_ascii=False, indent=4)
    
    async def _save(self):
        await asyncio.to_thread(self._write_file)

    async def set_state(self, chat_id: str | int, state: str | None):
        chat_id = str(chat_id)
        if chat_id not in self._states:
            self._states[chat_id] = {'state': None, 'data': {}}
        self._states[chat_id]['state'] = state
        await self._save()

    async def get_state(self, chat_id: str | int) -> str | None:
        return self._states.get(str(chat_id), {}).get('state')
    
    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        chat_id = str(chat_id)
        if chat_id not in self._states:
            self._states[chat_id] = {"state": None, "data": {}}
        self._states[chat_id]["data"].update(kwargs)
        await self._save()

    async def get_data(self, chat_id: str | int) -> dict:
        return self._states.get(str(chat_id), {}).get('data', {})

    async def clear_state(self, chat_id: str | int):
        chat_id = str(chat_id)
        if chat_id in self._states:
            del self._states[chat_id]
            await self._save()


class FSMContext:
    def __init__(self, storage: BaseStorage, chat_id: str | int):
        self.storage = storage
        self.chat_id = str(chat_id)
    
    async def set_state(self, state: str | None):
        await self.storage.set_state(self.chat_id, state)

    async def get_state(self) -> str | None:
        return await self.storage.get_state(self.chat_id)

    async def update_data(self, **kwargs):
        await self.storage.update_data(self.chat_id, **kwargs)

    async def get_data(self) -> dict:
        return await self.storage.get_data(self.chat_id)

    async def clear_state(self):
        await self.storage.clear_state(self.chat_id)