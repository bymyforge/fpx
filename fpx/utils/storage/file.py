import json
import asyncio
import os
from .base import BaseStorage


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