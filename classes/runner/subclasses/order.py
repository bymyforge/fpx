


class OrderRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_order_cache(self):
        '''
        Обновляет кеш заказов в раннере
        '''
        orders = await self.runner._account.profile.get_my_sells(25)
        result = []
        for order in orders:
            o = {
                'id': order.order_id,
                'time': order.order_time,
                'client_name': order.client_name,
                'price': order.price,
                'name': order.name,
                'status': order.status
            }
            result.append(o)
        self.runner._cache['old_orders'] = self.runner._cache['orders']
        self.runner._cache['orders'] = result

    async def _compare_order_cache(self):
        '''
        Сравнивает старый и новый кеш заказов
        '''
        result = []
        if self.runner._cache['orders'] != self.runner._cache['old_orders']:
            for order in self.runner._cache['orders']:
                if order not in self.runner._cache['old_orders']:
                    result.append(order)
        return result

    async def _check_orders(self):
        await self.runner._order._update_order_cache()
        orders = await self.runner._order._compare_order_cache()
        if orders:
            for order in orders:
                for handler in self.runner._handlers['order']:
                    await handler(order)
                if order['status'] == 'Закрыт':
                    for handler in self.runner._handlers['confirmed_order']:
                        await handler(order)
                elif order['status'] in('Оплачено', 'Оплачен'):
                    for handler in self.runner._handlers['new_order']:
                        await handler(order)
                elif order['status'] == 'Возврат':
                    for handler in self.runner._handlers['refund']:
                        await handler(order)