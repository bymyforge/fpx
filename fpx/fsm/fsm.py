from fpx.utils.storage.base import BaseStorage


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
