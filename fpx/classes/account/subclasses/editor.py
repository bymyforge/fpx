import asyncio

from fpx.utils import errors as fpx_err


class FunPayEditor:
    def __init__(self, account):
        self._account = account

    async def set_lot_secrets(self, lot_id: int | str, secrets: list[str], rewrite: bool = False):
        '''
        Обновить/Перезаписать данные автовыдачи лота.
        Посмотреть текущие данные можно FunPayTools.account.lot.get_lot_secrets().

        Args:
            lot_id (int | str): ID лота
            secrets (list[str]): Список товаров автовыдачи
            rewrite (bool) = False: False если добавить к текущей автовыдаче
                новый товар, True если перезаписать полностью
        Returns:
            bool: True - Данные обновлены.
        Raises:
            FpxLotEditingError: Секреты не изменились
            FpxRequestError: Плохое соединение с интернетом/сервер не ответил
        '''
        lot = await self._account.lot._get_lot_editor_details(lot_id)
        lot.fields['auto_delivery'] = 'on'
        secret_str = '\n'.join(secrets)
        if rewrite:
            lot.fields['secrets'] = secret_str
        else:
            secret_str = lot.fields.get('secrets', '') + '\n' + secret_str
            lot.fields['secrets'] = secret_str
        response = await self._account._client.edit_lot(lot, active=True)
        if response.status_code == 200:
            await asyncio.sleep(0.5)
            new_lot = await self._account.lot._get_lot_editor_details(lot_id)
            if new_lot.fields.get('secrets') == secret_str:
                return True
            print(repr(new_lot.fields.get('secrets')))
            print(repr(secret_str))
            raise fpx_err.FpxLotEditingError(f"Секреты на сайте остались старыми: {new_lot.fields.get('secrets')}")
        raise fpx_err.FpxRequestError(f"Ошибка изменения секретов. Статус: {response.status_code}")

    async def change_lot_price(self, lot_id: int | str, new_price: str):
        '''
        Изменяет цену лота.

        Args:
            lot_id (str | int): Айди лота
            new_price (str): Новая цена лота
        Returns:
            bool: True - цена изменилась.
        Raises:
            FpxLotEditingError: Цена не изменилась
            FpxRequestError: Плохое соединение с интернетом/сервер не ответил
        '''
        lot = await self._account.lot._get_lot_editor_details(lot_id)
        lot.fields['price'] = new_price
        response = await self._account._client.edit_lot(lot, active=True)
        if response.status_code == 200:
            await asyncio.sleep(0.5)
            new_lot = await self._account.lot._get_lot_editor_details(lot_id)
            if str(new_lot.fields.get('price')) == str(new_price):
                return True
            raise fpx_err.FpxLotEditingError(f"Цена на сайте осталась старой: {new_lot.fields.get('price')}")
        raise fpx_err.FpxRequestError(f"Ошибка изменения цены. Статус: {response.status_code}")

    async def toggle_off_lot(self, lot_id):
        '''
        Выключает лот.

        Args:
            lot_id (str | int): Айди лота
        Returns:
            bool: True - лот выключен
        Raises:
            FpxRequestError: Сервер не ответил
        '''
        lot = await self._account.lot._get_lot_editor_details(lot_id)
        response = await self._account._client.edit_lot(lot)
        if response.status_code == 200:
            return True
        raise fpx_err.FpxRequestError('Ошибка отправки запроса на изменение деталей лота')

    async def toggle_on_lot(self, lot_id):
        '''
        Включает лот.

        Args:
            lot_id (str | int): Айди лота
        Returns:
            bool: True - лот включен
        Raises:
            FpxRequestError: Сервер не ответил
        '''
        lot = await self._account.lot._get_lot_editor_details(lot_id)
        response = await self._account._client.edit_lot(lot, active=True)
        if response.status_code == 200:
            return True
        raise fpx_err.FpxRequestError('Ошибка отправки запроса на изменение деталей лота')
