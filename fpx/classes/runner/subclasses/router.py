


class Router:
    def __init__(self):
        self._handlers = {
            'message': [],
            'order': [],
            'confirmed_order': [],
            'new_order': [],
            'refund': [],
            'review': [],
            'lot_category': [],
            'chip_category': [],

            # системные
            'startup': [],
            'flood': []
        }
        
    def on_message(self, text: str | None = None, mapping: dict[str, str] | None = None):
        '''Декоратор отслеживает новые сообщения.
        
        Args:
            - text (str): Текст, по которому фильтруется отображение новых сообщений.
            - mapping (dict): Словарь 'ключ': 'значение' для упрощённых ответов, вводи 'Привет' и 'Привет, работаю' и теперь скрипт будет всегда отвечать за тебя Привет, работаю когда тебе пишут привет. Вводи сколько угодно маппинга    

        Returns:
            Message: Объект, содержащий:    
                - sender (str): Имя отправителя     
                - chat_id (str): Айди чата (node id)    
                - last_msg (str): Сообщение, которое было отправлено в этом чате    
                - is_system (bool): Системное ли сообщение      
                - anwer (method): При указании текста в аргументах, отвечает на сообщение       
        '''
        def decorator(func):
            self._handlers['message'].append({
                'function': func,
                'filter_text': text,
                'mapping': mapping
            })
            return func
        return decorator

    def on_orders(self, mapping: list[str] | None = None):
        '''
        Декоратор отслеживает все события заказов.
        Не рекомендуется использовать вместе с on_cofirmed_orders, on_new_order, on_refunded_orders во избежание дублирования событий.

        Returns:
            Order: Объект, содержащий:      
                - order_id (str): Уникальный ID заказа          
                - description (str): Описание лота
                - order_time (str): Время оплаты заказа     
                - client_name (str): Имя клиента
                - price (str): Цена товара     
                - status (str): Статус заказа   
                - name (str): Название товара   
                - anwer (method): При указании текста в аргументах, отвечает на сообщение       
        '''
        def decorator(func):
            self._handlers['order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator
    
    def on_confirmed_orders(self, mapping: list | None = None):
        '''
        Декоратор, который отслеживает только событие подтверждёния заказа.

        Returns:
            Order: Объект, содержащий:      
                - order_id (str): Уникальный ID заказа          
                - order_time (str): Время оплаты заказа     
                - client_name (str): Имя клиента
                - price (str): Цена товара     
                - status (str): Статус заказа   
                - name (str): Название товара   
                - anwer (method): При указании текста в аргументах, отвечает на сообщение       
        '''
        def decorator(func):
            self._handlers['confirmed_order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_new_order(self, mapping: list | None = None):
        '''
        Декоратор, который отслеживает только новые заказы.

        Returns:
            Order: Объект, содержащий:      
                - order_id (str): Уникальный ID заказа          
                - order_time (str): Время оплаты заказа     
                - client_name (str): Имя клиента
                - price (str): Цена товара     
                - status (str): Статус заказа   
                - name (str): Название товара   
                - anwer (method): При указании текста в аргументах, отвечает на сообщение       
        '''
        def decorator(func):
            self._handlers['new_order'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator
    
    def on_new_review(self):
        '''Декоратор отслеживает новые отзывы.

        Returns:
            CurReview: Объект, содержащий:        
                - text (str): Текст отзыва  
                - stars (int): Кол-во звёзд, оставленных под отзывом
                - author (str): Автор отзыва    
                - item_name (str): Заказ, под которым оставлен отзыв        
        '''
        def decorator(func):
            self._handlers['review'].append(func)
            return func
        return decorator

    def on_refunded_orders(self, mapping: list | None = None):
        '''
        Декоратор отслеживает события возврата заказов.

        Returns:
            Order: Объект, содержащий:      
                - order_id (str): Уникальный ID заказа          
                - order_time (str): Время оплаты заказа     
                - client_name (str): Имя клиента
                - price (str): Цена товара     
                - status (str): Статус заказа   
                - name (str): Название товара   
                - anwer (method): При указании текста в аргументах, отвечает на сообщение       
        '''
        def decorator(func):
            self._handlers['refund'].append({
                'function': func,
                'mapping': mapping
            })
            return func
        return decorator

    def on_lot_category(self):
        '''
        Декоратор отслеживает снижение цен на лоты.     

        Returns:
            CategoryLastLot: Объект, содержащий:        
                - price (float): Цена лота      
                - offer_id (str): Айди лота         
        '''
        def decorator(func):
            self._handlers['lot_category'].append(func)
            return func
        return decorator

    def on_chip_category(self):
        '''
        Декоратор отслеживает снижение цен на чипсах(коротких лотов под валюты).    

        Returns:
            CategoryLastLot: Объект, содержащий:    
                - price (float): Цена лота      
                - offer_id (str): Айди лота     
        '''
        def decorator(func):
            self._handlers['chip_category'].append(func)
            return func
        return decorator

    def on_startup(self):
        '''Декоратор отслеживает запуск раннера'''
        def decorator(func):
            self._handlers['startup'].append(func)
            return func
        return decorator

    def on_flood(self):
        '''Декоратор отслеживает флуд в системе'''
        def decorator(func):
            self._handlers['flood'].append(func)
            return func
        return decorator