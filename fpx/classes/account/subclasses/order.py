from fpx.models.account import Order
from fpx.utils import errors as fpx_err

class OrderManager:
    def __init__(self, account):
        self._account = account
    
    async def get_order_details(self, order_id):
        '''
        Функция запрашивает детали заказа из /orders/{order_id}/.

        Args:
            order_id (str | int): ID заказа
        Returns:
            Order: Объект с данными:  
                - order_id (str): ID заказа
                - status (str): Статус заказа.  
                - review (dict): Словарь с данными отзыва, который оставили к заказу.   
                - description (str): Строка с подробным описанием заказа    
                - chat_id (str): ID чата    
        Raises:
            FpxGetOrderInfoError: Ошибка запроса данных заказа
        '''
        try:
            stage = 'запроса данных FunPay'
            html = await self._account._client.get_order_info(order_id)
            stage = 'парсинга данных'
            data = self._account._parser.parse_order_page(html)
            stage = 'типизации данныз'
            order = Order(order_id=order_id, status=data['status'], review=data['review'], description=data['desc'], chat_id=data['chat_id'])
        except Exception as e:
            raise fpx_err.FpxGetOrderInfoError(f'При выполнении {stage} произошла ошибка: {e}')
        return order

    async def refund_order(self, order_id):
        '''
        Делает возврат заказа.

        Args:
            order_id (str | int): Айди заказа
        Returns:
            bool: True если возврат прошёл успешно. 
        Raises:
            FpxRefundError: Не удалось сделать возврат.  
        
        '''
        response = await self._account._client.refund_order(order_id)
        if response.status_code == 200:
            s = await self.get_order_details(order_id)
            status = s.status
            if status == 'Возврат':
                return True
            raise fpx_err.FpxRefundError(f'Невозможно сделать возврат, текущий статус: {status}')