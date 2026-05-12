


class AddonsManager:
    def __init__(self, account):
        self.account = account

    async def get_game_id(self, category_id):
        '''
        https://funpay.com/lots/{category_id}/trade
        '''
        html = await self.account.client.lot_menu_by_category(category_id)
        data = self.account.parser.parse_lot_menu(html)
        return data