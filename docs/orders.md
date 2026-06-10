# Заказы

Отслеживание заказов, автовыдача, возвраты.

---

## Хендлеры

### `@fp.router.on_orders(mapping=None)`

Все события заказов (оплата, подтверждение, возврат).

⚠️ Не используй вместе с узкими хендлерами — будет дублирование.

```python
@fp.router.on_orders()
async def any_order(order: Order):
    print(f'Заказ {order.order_id}, статус: {order.status}')
```

### `@fp.router.on_new_order(mapping=None)`

Только новые оплаченные заказы.

```python
@fp.router.on_new_order()
async def new_order(order: Order):
    print(f'Новый заказ #{order.order_id} от {order.client_name}')
    await order.answer(f'Заказ "{order.name}" принят!')
```

**mapping** — список ключевых слов. Хендлер сработает только если одно из слов есть в описании заказа:

```python
@fp.router.on_new_order(mapping=['ключ', 'key'])
async def auto_key(order: Order):
    await order.answer('Вот твой ключ: XXX-YYY-ZZZ')
```

### `@fp.router.on_confirmed_orders(mapping=None)`

Только подтверждённые заказы (покупатель нажал "Подтвердить выполнение").

```python
@fp.router.on_confirmed_orders()
async def confirmed(order: Order):
    await order.answer('Спасибо за подтверждение! Буду рад отзыву')
```

### `@fp.router.on_refunded_orders(mapping=None)`

Только возвраты.

```python
@fp.router.on_refunded_orders()
async def refunded(order: Order):
    print(f'Возврат: {order.order_id}')
```

---

## Объект Order

| Поле | Тип | Описание |
|------|-----|----------|
| `order_id` | `str` | ID заказа |
| `chat_id` | `str` | ID чата |
| `order_time` | `str` | Время заказа |
| `description` | `str` | Описание (что ввёл покупатель) |
| `client_name` | `str` | Ник покупателя |
| `price` | `float` | Цена |
| `amount` | `int` | Количество |
| `status` | `str` | Статус (Оплачен, Закрыт, Возврат) |
| `name` | `str` | Название товара |
| `category` | `str` | Категория |
| `review` | `dict` | Отзыв (если есть) |

### Методы

**`await order.answer(answer_text: str)`** — отправить сообщение в чат заказа. Поддерживает форматирование:
- `{order_id}` — ID заказа
- `{order_time}` — время
- `{client_name}` — ник покупателя
- `{order_name}` — название товара

---

## OrderManager (через account.order)

### `await fp.account.order.get_order_details(order_id)`

Полная информация о заказе со страницы `/orders/{id}/`.

```python
order = await fp.account.order.get_order_details('ABC123')
print(order.status)
print(order.description)
```

### `await fp.account.order.refund_order(order_id)`

Возврат денег по заказу.

```python
await fp.account.order.refund_order('ABC123')
```

Возвращает `True` если возврат прошёл. При ошибке — `FpxRefundError`.
