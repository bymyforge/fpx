from dataclasses import dataclass, field
from typing import Any

from fpx.utils import errors as fpx_err


@dataclass
class CurrentLotInfo:
    short_desc: str
    description: str
    price: float
    _client: Any = field(init=False, repr=False, default=None)
    async def edit_price(self, new_price):
        '''Изменяет цену лота'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurrentLotInfo не привязан к клиенту fpx')
        return await self._client.editor.change_lot_price(self.id, new_price)

    async def raise_lot(self):
        '''Поднимает все лоты'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurrentLotInfo не привязан к клиенту fpx')
        return await self._client.lot.raise_lots()

    async def deactivate(self):
        '''Выключает лот'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurrentLotInfo не привязан к клиенту fpx')
        return await self._client.editor.toggle_off_lot(self.id)

    async def activate(self):
        '''Включает лот'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurrentLotInfo не привязан к клиенту fpx')
        return await self._client.editor.toggle_on_lot(self.id)

@dataclass
class LotEditor:
    csrf_token: str
    form_created_at: str
    offer_id: str
    node_id: str
    location: str
    deleted: str
    fields: dict = field(default_factory=dict)

@dataclass
class LotInfo:
    name: str
    id: str
    _client: Any = field(init=False, repr=False, default=None)
    async def edit_price(self, new_price):
        '''Изменяет цену лота'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект LotInfo не привязан к клиенту fpx')
        return await self._client.editor.change_lot_price(self.id, new_price)

    async def raise_lot(self):
        '''Поднимает все лоты'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект LotInfo не привязан к клиенту fpx')
        return await self._client.lot.raise_lots()

    async def deactivate(self):
        '''Выключает лот'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект LotInfo не привязан к клиенту fpx')
        return await self._client.editor.toggle_off_lot(self.id)

    async def activate(self):
        '''Включает лот'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект LotInfo не привязан к клиенту fpx')
        return await self._client.editor.toggle_on_lot(self.id)

@dataclass
class CategoryLastLot:
    category_id: str
    filtration: str
    price: float
    offer_id: str
    owner_username: str