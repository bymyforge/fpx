from fpx.models.account import UserData, Order, Profile, CurReview
from fpx.models.lots import LotInfo

from fpx.utils import errors as fpx_err


class ProfileManager:

    def __init__(self, account):
        self._account = account

    async def get_user_data(self):
        '''
        Запрашивает данные юзера, сохраняет их в кеш.
        
        Returns:
            UserData: Объект с данными юзера:   
                - user_id (str): ID юзера.  
                - csrf_token (str): Нужен для любого post запроса на funpay.  
        Raises:
            FpxGetUserDataError: ошибка запроса данных юзера  
        '''
        try:
            stage = 'запроса данных FunPay'
            html = await self._account._client.get_main_menu()
            stage = 'парсинга данных'
            data = self._account._parser.parse_main_menu(html)
            stage = 'типизации данных'
            self._account.data.username = data['username']
            self._account.data.user_id = data['user-id']
            self._account.data._csrf_token = data['csrf-token']
            user_data = UserData(csrf_token=data['csrf-token'], user_id=data['user-id'])
        except Exception as e:
            raise fpx_err.FpxGetUserDataError(f'При выполнении {stage} произошла ошибка: {e}')
        return user_data

    async def get_my_sells(self, limit:int=0):
        '''
        Запрашивает страницу продаж юзера.

        Args:
            limit (int): Лимит заказов, которые нужно вернуть(если 0, то вернёт все заказы).
        Returns:
            list: Список объектов, каждый содержит в себе:      
                - order_id (str): ID заказа.        
                - order_time (str): Время создания заказа.      
                - client_name (str): Имя клиента.       
                - price (float): Сумма заказа.      
                - amount (int): Кол-во штук заказа (1 по дефолту).      
                - topup_nickname (str): Данные, на которые отправлять пополнение. (ник, ссылка игрока и тд.)    
                - status (str): Статус заказа.  
                - name (str): Название заказа.  
                - category (str): Категория заказа.   
        Raises:
            FpxGetUserSellsError: Ошибка запроса продаж  
        '''
        try:
            stage = 'запроса данных FunPay'
            html = await self._account._client.get_my_sells()
            stage = 'парсинга данных'
            data = self._account._parser.parse_my_sells(html)
            counter = 0
            result = []
        except Exception as e:
            raise fpx_err.FpxGetUserSellsError(f'При выполнении {stage} произошла ошибка: {e}')
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
                category=i['category'],
                amount=i['amount'],
                topup_data=i.get('topup_data')
            )
            result.append(order)
            counter += 1
        return result

    async def profile(self, user_id=None):
        '''
        Запрашивает профиль юзера.
        Args:
            user_id (str | int): Можно не передавать, если None, сама узнает айди владельца сессии и запросит данные о нём. Айди юзера.
        Returns:
            Profile: Объект, с данными:  
                - category_ids (list): ID категорий, в которых у юзера выставлены лоты.   
                - lots (list): Список словарей с лотами юзера юзера {lot['name']: lot['id']}.   
                - reviews (list): Список объектов отзыва CurReview с данными:  
                    - text (str): Текст отзыва. 
                    - stars (int): Кол-во звёзд в отзыве (1-5). 
                    - author (str): Автор отзыва.   
                    - item_name (str): Название заказа, под которым оставлен отзыв.     
        Raises:
            FpxGetProfileError: Ошибка запроса профиля
        '''
        target_id = user_id or self._account.data.user_id
        if not target_id:
            target = await self.get_user_data()
            target_id = target.user_id
        try:
            step = 'запроса данных FunPay'
            html = await self._account._client.get_user_profile(target_id)
            step = 'парсинга данных'
            data = self._account._parser.parse_profile(html)
            step = 'типизации данных'
            lots_list = [LotInfo(name=lot['name'], id=lot['id']) for lot in data['lots']]
            reviews = [CurReview(text=rev['text'], stars=rev['stars'], author=rev['author'], order_id=rev['order_id']) for rev in data['reviews']]
            profile = Profile(category_ids=data['category-ids'], lots=lots_list, reviews=reviews)
        except Exception as e:
            raise fpx_err.FpxGetProfileError(f'При выполнении {step} произошла ошибка: {e}')
        return profile

    async def get_balance(self):
        '''
        Собирает баланс аккаунта.

        Returns:
            Balance: Объект с валютами:    
                - rub (float): Баланс в рублях  
                - usd (float): Баланс в долларах  
                - eur (float): Баланс в евро    
        Raises:
            FpxGetProfileError: Ошибка сбора баланса
        '''
        try:
            step = 'запрос данных FunPay'
            html = await self._account._client.get_finance_page()
            step = 'парсинг данных'
            balance = self._account._parser.parse_finanses(html)
        except Exception as e:
            raise fpx_err.FpxGetProfileError(f'При сборе баланса, выполняя {step} произошла ошибка: {e}')
        return balance