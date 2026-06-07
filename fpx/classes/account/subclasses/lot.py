from fpx.models.lots import LotEditor, CurrentLotInfo
from fpx.utils import errors as fpx_err


class LotManager:
    def __init__(self, account):
        self._account = account

    async def _get_lot_editor_details(self, lot_id):
        '''
        Не для обычного использования! (функция для изменения лота)
        Получает данные для изменения лота с https://funpay.com/lots/offerEdit?offer={lot_id}.

        Args:
            lot_id (str | int): Айди лота
        Returns:
            LotEditor: Возвращает объект с:
                - csrf_token (str): нужен для любого post запроса.  
                - form_created_at (str): время создания формы изменения лота.  
                - offer_id (str): Айди оффера(лота).  
                - node_id (str): Айди нода.  
                - location (str): Обычно пустой.  
                - deleted (str): Обычно пустой.  
                - fields (dict): Словарь с филдами, нет фиксированного кол-ва филдов, просто отправляйте все.  
        Raises:
            FpxGetLotEditorInfoError: ошибка поулучения данных редактора
        '''
        try:
            stage = 'запроса данных с FunPay'
            html = await self._account._client.get_lot_editor_data(lot_id)
            stage = 'парсинга данных'
            data = self._account._parser.parse_edit_lot_page(html)
        except Exception as e:
            raise fpx_err.FpxGetLotEditorInfoError(f'При выполнении {stage} произошла ошибка: {e}')
        base_fields = ['csrf_token', 'form_created_at', 'offer_id', 'node_id', 'location', 'deleted']
        main_data = {k: v for k, v in data.items() if k in base_fields}
        other_fields = {k: v for k, v in data.items() if k not in base_fields}
        lot = LotEditor(**main_data, fields=other_fields)
        return lot

    async def get_lot_info(self, lot_id):
        '''
        Собирает данные лота.

        Args:
            lot_id (str | int): ID лота.
        Returns:
            CurrentLotInfo: Объект с этими данными:  
                - short_desc (str): Краткое описание.   
                - description (str): Полное описание.  
                - price (float): Цена лота.  
        Raises:
            FpxGetLotInfoError: Ошибка запроса данных лота
        '''
        try:
            stage = 'запроса данных'
            html = await self._account._client.get_lot_info(lot_id)
            stage = 'парсинга данных'
            data = self._account._parser.parse_current_lot_menu(html)
            stage = 'типизации данных'
            lot = CurrentLotInfo(
                short_desc=data['short_desc'],
                description=data['description'],
                price=float(data['price'])
            )
        except Exception as e:
            raise fpx_err.FpxGetLotInfoError(f'При выполнении {stage} произошла ошибка: {e}')
        return lot

    async def raise_lots(self):
        '''
        Поднимает все лоты.

        Returns:
            list: Ответы от сервера. 
        Raises:
            FpxRaisingLotError: Лот не поднят. 
        '''
        if not self._account.data._csrf_token:
            await self._account.profile.get_user_data()
        try:
            profile = await self._account.profile.profile()
            category_list = profile.category_ids
            if not category_list:
                raise fpx_err.FpxRaisingLotError('Нам нечего поднимать')
            response = []
            for node_id in category_list:
                game_id = await self._account.addons.get_game_id(node_id)
                response.append(await self._account._client.raise_lot(node_id, game_id))
            return response
        except Exception as e:
            raise fpx_err.FpxRaisingLotError(message=e)