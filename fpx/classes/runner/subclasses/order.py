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
                    order.finded_mapping = trigger
                    matched = True
                    break
                if not matched:
                    return False
        sig = inspect.signature(h_func)
        has_state = False
        for param in sig.parameters.values():
            if param.annotation == FSMContext:
                has_state = True
                break
        if has_state:
            await h_func(order, state_ctx)
        else:
            await h_func(order)

    async def _check_trigger_for_command(self, order: Order, state_ctx: FSMContext):
        if order.description is None:
            return False
        for cmd_handler in self.runner.handler._handlers['order_command']:
            target_command = cmd_handler['trigger_command']
            target_command_lower = {k.lower(): v for k, v in target_command.items()}
            target_function = None
            for command_name in target_command_lower:
                if command_name in order.description.lower():
                    target_function = target_command_lower[command_name]
                    order.finded_mapping = command_name
                    break 
            if target_function is None:
                continue
            sig = inspect.signature(target_function)
            has_state = False
            for param in sig.parameters.values():
                if param.annotation == FSMContext:
                    has_state = True
                    break
            if has_state:
                await target_function(order, state_ctx)
            else:
                await target_function(order)
            return True
        return False

    async def _trigger_order_handlers(self, order: Order):
        state_ctx = FSMContext(self.runner.storage, order.chat_id)
        status = order.status.lower()
        for handler in self.runner.handler._handlers['order']:
            await self._check_handler(handler, order, state_ctx)
        if status in ('закрыт', 'closed', 'закрито'):
            for handler in self.runner.handler._handlers['confirmed_order']:
                await self._check_handler(handler, order, state_ctx)
        elif status in ('оплачен', 'оплачено', 'paid', 'відкрито'):
            for handler in self.runner.handler._handlers['new_order']:
                await self._check_handler(handler, order, state_ctx)
            await self._check_trigger_for_command(order, state_ctx)
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