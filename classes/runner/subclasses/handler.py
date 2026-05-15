


class Handlers:
    def __init__(self, runner):
        self.runner = runner
        
    def on_message(self):
        '''Декоратор возвращает новые сообщения'''
        def decorator(func):
            self.runner._handlers['message'].append(func)
            return func
        return decorator

    def on_orders(self):
        '''Декоратор возвращает все события заказов'''
        def decorator(func):
            self.runner._handlers['order'].append(func)
            return func
        return decorator
    
    def on_confirmed_orders(self):
        '''Декоратор, который возвращает только событие заказ подтверждён'''
        def decorator(func):
            self.runner._handlers['confirmed_order'].append(func)
            return func
        return decorator

    def on_new_order(self):
        '''Декоратор, который возвращает только события новый заказ'''
        def decorator(func):
            self.runner._handlers['new_order'].append(func)
            return func
        return decorator
    
    def on_new_review(self):
        '''Декоратор отслеживает новые отзывы'''
        def decorator(func):
            self.runner._handlers['review'].append(func)
            return func
        return decorator

    def on_refunded_orders(self):
        '''Декоратор отслеживает возвраты заказов'''
        def decorator(func):
            self.runner._handlers['refund'].append(func)
            return func
        return decorator