import json

from .base import BaseStorage


class RedisStorage(BaseStorage):
    '''
    Хранилище FSM на редис
    Внимание. при конкурентном доступе к одному chat_id
    возможна потеря данных (race condition).
    Для высоких нагрузок используйте Redis Lua-скрипты.
    '''
    def __init__(self, url: str = "redis://localhost:6379", prefix: str = 'fpx'):
        try:
            from redis.asyncio import Redis  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "Redis не установлен. Установи: pip install fpx-engine[redis]"
            )
        self._redis = Redis.from_url(url, decode_responses=True)
        self._prefix = prefix

    def _key(self, chat_id: str) -> str:
        return f'{self._prefix}:fsm:{chat_id}'

    async def set_state(self, chat_id: str | int, state: str | None):
        key = self._key(str(chat_id))
        data = await self.get_data(chat_id)
        await self._redis.set(key, json.dumps({'state': state, 'data': data}))

    async def get_state(self, chat_id: str | int) -> str | None:
        raw = await self._redis.get(self._key(str(chat_id)))
        if not raw:
            return None
        return json.loads(raw).get("state")

    async def update_data(self, chat_id: str | int, **kwargs):
        """Обновляет данные для чата.

        Warning: НЕ потокобезопасно. Если два хендлера
        одновременно пишут данные в один чат, одно из
        изменений может пропасть, не критично на слабых оборотах.
        """
        key = self._key(str(chat_id))
        current = await self.get_data(chat_id)
        current.update(kwargs)
        state = await self.get_state(chat_id)
        await self._redis.set(key, json.dumps({"state": state, "data": current}))

    async def get_data(self, chat_id: str | int) -> dict:
        raw = await self._redis.get(self._key(str(chat_id)))
        if not raw:
            return {}
        return json.loads(raw).get("data", {})

    async def clear_state(self, chat_id: str | int):
        await self._redis.delete(self._key(str(chat_id)))
