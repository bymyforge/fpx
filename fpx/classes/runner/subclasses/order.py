import inspect

from fpx.models.account import Order
from fpx.fsm import FSMContext


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

    async def _check_handler(self, handler, order, state_ctx):
        h_func = handler['function']
        if handler.get('mapping') is not None:
            msg_text = order.description.lower()
            matched = False
            for trigger in handler['mapping']:
                if trigger.lower() in msg_text:
                    matched = True
                    break
                if not matched:
                    return False
        sig = inspect.signature(h_func)
        if len(sig.parameters) >= 2:
            await h_func(order, state_ctx)
        else:
            await h_func(order)

    async def _trigger_order_handlers(self, order: Order):
        state_ctx = FSMContext(self.runner.storage, order.chat_id)
        status = order.status.lower()
        for handler in self.runner.handler._handlers['order']:
            await self._check_handler(handler, order, state_ctx)
        if status in ('закрыт', 'closed', 'закрито'):
            for handler in self.runner.handler._handlers['confirmed_order']:
                await self._check_handler(handler, order, state_ctx)
        elif status in('оплачен', 'оплачено', 'paid', 'opened', 'відкрито'):
            for handler in self.runner.handler._handlers['new_order']:
                await self._check_handler(handler, order, state_ctx)
        elif status in ('возврат', 'повернення', 'refund'):
            for handler in self.runner.handler._handlers['refund']:
                await self._check_handler(handler, order, state_ctx)

    async def _check_orders(self):
        await self.runner._order._update_order_cache()
        orders = await self.runner._order._compare_order_cache()
        if orders:
            for order in orders:
                order_info = await self.runner._account.order.get_order_details(order.order_id)
                order.description = order_info.description
                order.chat_id = order_info.chat_id
                order._client = self.runner
                await self._trigger_order_handlers(order)