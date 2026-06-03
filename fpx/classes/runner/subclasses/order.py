from fpx.models.account import Order


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
                'order_id': order.order_id,
                'order_time': order.order_time,
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
                    result.append(Order(**order))
        return result

    async def _check_handler(self, handler, order):
        if handler.get('mapping') is None:
            await handler['function'](order)
            return
        else:
            matched = False
            for trigger in handler['mapping']:
                if trigger.lower() in order.description.lower():
                    matched = True
                    break
            if matched:
                await handler['function'](order)

    async def _trigger_order_handlers(self, order: Order):
        for handler in self.runner.handler._handlers['order']:
            await self._check_handler(handler, order)
        status = order.status.lower()
        if status in ('закрыт', 'closed', 'закрито'):
            for handler in self.runner.handler._handlers['confirmed_order']:
                await self._check_handler(handler, order)
        elif status in('оплачен', 'оплачено', 'paid', 'opened', 'відкрито'):
            for handler in self.runner.handler._handlers['new_order']:
                await self._check_handler(handler, order)
        elif status in ('возврат', 'повернення', 'refund'):
            for handler in self.runner.handler._handlers['refund']:
                await self._check_handler(handler, order)

    async def _check_orders(self):
        await self.runner._order._update_order_cache()
        orders = await self.runner._order._compare_order_cache()
        if orders:
            for order in orders:
                order_info = await self.runner._account.order.get_order_details(order.order_id)
                order.description = order_info.description
                order.chat_node_id = order_info.chat_node_id
                order._client = self.runner
                await self._trigger_order_handlers(order)