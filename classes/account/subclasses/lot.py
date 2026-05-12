from models.lots import LotEditor, CurrentLotInfo
from utils.errors import NullData, RaisingLotError


class LotManager:
    def __init__(self, account):
        self.account = account

    async def get_lot_editor_details(self, lot_id):
        '''
        Get data from https://funpay.com/lots/offerEdit?offer={lot_id}
        '''
        html = await self.account.client.get_lot_editor_data(lot_id)
        data = self.account.parser.parse_edit_lot_page(html)
        base_fields = ['csrf_token', 'form_created_at', 'offer_id', 'node_id', 'location', 'deleted']
        main_data = {k: v for k, v in data.items() if k in base_fields}
        other_fields = {k: v for k, v in data.items() if k not in base_fields}
        lot = LotEditor(**main_data, fields=other_fields)
        return lot

    async def get_lot_info(self, lot_id):
        '''
        Func gets lot data:  
            short_desc: str  
            description: str  
            price: float  
        '''
        html = await self.account.client.get_lot_info(lot_id)
        data = self.account.parser.parse_current_lot_menu(html)
        lot = CurrentLotInfo(
            short_desc=data['short_desc'],
            description=data['description'],
            price=float(data['price'])
        )
        return lot

    async def raise_lots(self):
        '''
        The function raises your lots and returns a response from the FunPay server.
        '''
        if not self.account.csrf_token:
            await self.account.profile.get_user_data()
        try:
            profile = await self.account.profile.profile()
            category_list = profile.category_ids
            if not category_list:
                raise NullData('I cant raise none')
            response = []
            for node_id in category_list:
                game_id = await self.account.addons.get_game_id(node_id)
                response.append(await self.account.client.raise_lot(node_id, game_id, self.account.csrf_token))
            return response
        except Exception as e:
            raise RaisingLotError()