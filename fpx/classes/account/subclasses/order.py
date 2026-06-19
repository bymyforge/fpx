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
            order = Order(
                order_id=order_id,
                status=data['status'],
                review=data['review'],
                description=data['desc'],
                chat_id=data['chat_id']
            )
        except Exception as e:
            raise fpx_err.FpxGetOrderInfoError(f'При выполнении {stage} произошла ошибка: {e}')
        return order

    async def find_orders_by_buyer_name(self, buyer_name: str, full_info: bool = True):
        '''
        Ищет все заказы по имени покупателя.

        Args:
            buyer_name (str): Имя покупателя.
            full_info (bool): Спрашивает показывать ли полную информацию
            по каждому заказу (требует дополнительный запрос).
            True по дефолту
        Returns:
            list[Order]: Список объектов Order, которые содержат:
                - order_id (str): ID заказа
                - order_time (str): Время заказа
                - client_name (str): Имя покупателя
                - price (float): Сумма заказа
                - status (str): Статус заказа
                - name (str): Название купленного лота
                - category (str): Категория заказа
                - amount (int): Кол-во штук заказа
                - topup_data (str): Данные пополнения (ссылка, ник, тп)
                - review (dict): Словарь с данными отзыва, который оставили к заказу.
                - description (str): Строка с подробным описанием заказа
                - chat_id (str): ID чата
        Raises:
            FpxGetOrderInfoError: Ошибка запроса данных заказа
        '''
        stage = 'запросе данных'
        try:
            orders = await self._account.profile.get_my_sells()
            good_orders = []
            stage = 'типизации данных'
            for order in orders:
                if order.client_name == buyer_name:
                    if full_info is True:
                        full_order = await self.get_order_details(order.order_id)
                        order.chat_id = full_order.chat_id
                        order.description = full_order.description
                        order.review = full_order.review
                    good_orders.append(order)
        except Exception as e:
            raise fpx_err.FpxGetOrderInfoError(f'При {stage} произошла ошибка: {e}')
        return good_orders


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
