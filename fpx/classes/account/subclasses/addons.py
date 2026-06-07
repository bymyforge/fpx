
from fpx.utils import errors as fpx_err


class AddonsManager:
    def __init__(self, account):
        self._account = account

    async def get_game_id(self, category_id: str):
        """
        Получает game_id.

        Args:
            category_id (str | int): ID подкатегории.
                
        Returns:    
            str | int: ID игры.

        Raises:
            FpxGetGameIDError: Ошибка запроса ID игры
        """
        try:
            stage = 'запроса данных категории с FunPay'
            html = await self._account._client.lot_menu_by_category(category_id)
            stage = 'парсинга данных'
            data = self._account._parser.parse_lot_menu(html)
        except Exception as e:
            raise fpx_err.FpxGetGameIDError(f'При выполнении {stage} произошла ошибка: {e}')
        return data