


class FunPayEditor:
    def __init__(self, account):
        self.account = account

    async def change_lot_price(self, lot_id, new_price):
        '''
        Func charge lot price
        '''
        