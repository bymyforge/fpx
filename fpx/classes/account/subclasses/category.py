from datetime import datetime

from fpx.models.lots import CategoryLastLot

class CategoryManager:
    def __init__(self, account):
        self._account = account

    async def get_lot_category_last_lot(self, lot_category_id):
        '''
        Находит самый дешевый лот в категории по каждому из фильтров.  

        Args:
            lot_category_id (int | str): ID категории лота      

        Returns:
            List[CategoryLastLot]: Объект, содержащий в себе:     
                - category_id (str): ID категории       
                - filtration (str): Название фильтра    
                - price (float): Цена лота      
                - offer_id (str): ID лота       
                - owner_username (str): Юзернейм владельца лота         
        '''
        html = await self._account.client.get_lot_category(lot_category_id)
        data = self._account._parser.parse_category_page(html)
        result = []
        for e in data:
            result.append(CategoryLastLot(category_id=lot_category_id, **e))
        return result

    async def get_chip_category_last_lot(self, chip_category_id):
        '''
        Находит самый дешевый лот краткий в категории по каждому из фильтров.  

        Args:
            lot_category_id (int | str): ID категории лота          

        Returns:
            List[CategoryLastLot]: Объект, содержащий в себе:          
                - category_id (str): ID категории   
                - filtration (str): Название фильтра    
                - price (float): Цена лота  
                - offer_id (str): ID лота   
                - owner_username (str): Юзернейм владельца лота   
        '''
        html = await self._account.client.get_chip_category(chip_category_id)
        data = self._account._parser.parse_category_page(html)
        result = []
        for e in data:
            result.append(CategoryLastLot(category_id=chip_category_id, **e))
        return result