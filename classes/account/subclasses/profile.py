from models.account import UserData, Order, Profile
from models.lots import LotInfo


class ProfileManager:

    def __init__(self, account):
        self.account = account

    async def get_user_data(self):
        '''
        Func gets user data, and save it to cache
            user_id
            csrf_token
        '''
        html = await self.account.client.get_main_menu()
        data = self.account.parser.parse_main_menu(html)
        self.account.user_id = data['user-id']
        self.account.csrf_token = data['csrf-token']
        user_data = UserData(csrf_token=data['csrf-token'], user_id=data['user-id'])
        return user_data

    async def get_my_sells(self, limit:int=0):
        '''
        Accept limit of orders arg, can be null(return all orders)
        Func get https://funpay.com/orders/trade
        Returns list of objects with orders
            order_id: str
            order_time: str
            client_name: str
            price: float
            status: str
            name: str
            category: str
        '''
        html = await self.account.client.get_my_sells()
        data = self.account.parser.parse_my_sells(html)
        counter = 0
        result = []
        if limit > 0:
            counter += 1
        for i in data:
            if limit != 0 and counter > limit:
                break
            order = Order(
                order_id=i['order-id'],
                order_time=i['order-time'],
                client_name=i['client-name'],
                price=i['price'],
                status=i['status'],
                name=i['name'],
                category=i['category']
            )
            result.append(order)
            counter += 1
        return result

    async def profile(self, user_id=None):
        '''
        Function gets user info  
        Takes user_id, nullable  
        If user_id is null, the value will be your session user_id  
        Returns object with 
            category_ids(node_id)
            lots[{lot['name']: lot['id']}]
        https://funpay.com/users/{user_id}/  
        '''
        target_id = user_id or self.account.user_id
        if not target_id:
            target = await self.get_user_data()
            target_id = target.user_id
        html = await self.account.client.get_user_profile(target_id)
        data = self.account.parser.parse_profile(html)
        lots_list = [LotInfo(name=lot['name'], id=lot['id']) for lot in data['lots']]
        profile = Profile(category_ids=data['category-ids'], lots=lots_list)
        return profile

    async def get_balance(self):
        '''
        The function calls the account balance, returns an object with values:  
            rub: float  
            usd: float  
            eur: float  
        '''
        html = await self.account.client.get_finance_page()
        balance = self.account.parser.parse_finanses(html)
        return balance