

from fpx.models.lots import CategoryLastLot

class CategoryManager:
    def __init__(self, account):
        self._account = account

    async def get_lot_category_last_lot(self, lot_category_id):
        '''
        Находит самый дешевый лот в категории.  

        Args:
            lot_category_id (int | str): ID категории лота      

        Returns:
            CategoryLastLot: Объект, содержащий в себе:     
                - price (float): Цена лота  
                - offer_id (str): ID лота   
        '''
        html = await self._account.client.get_lot_category(lot_category_id)
        data = self._account.parser.parse_category_page(html)
        return CategoryLastLot(**data)

    async def get_chip_category_last_lot(self, chip_category_id):
        '''
        Находит самый дешевый лот в категории.  

        Args:
            lot_category_id (int | str): ID категории лота      

        Returns:
            CategoryLastLot: Объект, содержащий в себе:     
                - price (float): Цена лота  
                - offer_id (str): ID лота   
        '''
        html = await self._account.client.get_chip_category(chip_category_id)
        data = self._account.parser.parse_category_page(html)
        return CategoryLastLot(**data)