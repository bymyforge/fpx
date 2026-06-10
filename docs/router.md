# Роутер и хендлеры

Роутер — это штука которая связывает события с твоими функциями. Все декораторы висят на `fp.router`. Также есть методы для регистрации команд.

---

## Сообщения

### `@fp.router.on_message()`

Самый главный декоратор. Ловит все новые сообщения в чатах.

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `text` | `str` | Срабатывает если сообщение **начинается** с этого текста |
| `contains` | `str` или `list[str]` | Срабатывает если в сообщении есть эти слова |
| `regex` | `str` или `list[str]` | Регулярка (через `re.search`) |
| `custom` | `Callable` | Своя функция-проверка, должна вернуть `True`/`False` |
| `mapping` | `dict[str, str]` | Словарь `{'триггер': 'ответ'}`, ответит автоматически |
| `state` | `str` | Сработает только если у чата этот стейт FSM |
| `ignore_chat_id` | `str`, `int` или `list` | Черный список чатов (игнорит эти айди) |
| `ignore_sender` | `str` или `list[str]` | Черный список юзеров |
| `priority` | `int` | Приоритет, чем больше — тем раньше проверяется |

**В хендлер прилетает объект `Message`:**

```python
@fp.router.on_message()
async def any_msg(message: Message):
    print(f'{message.sender}: {message.text}')
```

**Пример с фильтрами:**

```python
@fp.router.on_message(text='!привет')
async def cmd_hello(message: Message):
    await message.answer('Привет')

@fp.router.on_message(contains=['купить', 'заказать'])
async def buy_intent(message: Message):
    await message.answer('Хочешь купить? Пиши !товар')

@fp.router.on_message(regex=r'^id\d+$')
async def by_regex(message: Message):
    await message.answer('Нашёл ID')

@fp.router.on_message(mapping={'привет': 'Привет!', 'как дела': 'Норм'})
async def mapped(message: Message):
    # ответ уже отправлен автоматически, этот хендлер всё равно вызовется
    pass
```

**Совет:** mapping отвечает автоматически, но хендлер тоже вызывается. Если mapping сработал — не забудь поставить `return` если не хочешь чтобы дальнейший код выполнялся.

---

## Команды сообщений

### `fp.router.message_commands(dict)`

Регистрирует команды для чата. Ключ — команда (например `!start`), значение — асинхронная функция.

```python
async def start_cmd(message: Message):
    await message.answer('Привет, введи ник')

async def help_cmd(message: Message):
    await message.answer('Команды: !start, !help')

fp.router.message_commands({
    '!start': start_cmd,
    '!help': help_cmd
})
```

В функцию-команду автоматически передаются:
- `message: Message` — если параметр аннотирован как `Message` или называется `message`
- `state: FSMContext` — если параметр аннотирован как `FSMContext`
- `Dependency(...)` — зависимости, смотри пример ниже

**Пример с Dependency:**

```python
from fpx import Dependency

async def get_user(message: Message):
    return {'name': message.sender, 'vip': True}

async def vip_cmd(message: Message, user: dict = Dependency(get_user)):
    if user['vip']:
        await message.answer('Ты VIP')

fp.router.message_commands({'!vip': vip_cmd})
```

Команды проверяются **до** обычных `on_message` хендлеров. Если команда сработала — обычные хендлеры для этого сообщения не вызываются.

---

## Заказы

### `@fp.router.on_orders(mapping=None)`

Ловит **все** события заказов (оплата, подтверждение, возврат). Не рекомендуется использовать вместе с узкими хендлерами чтобы избежать дублирования.

```python
@fp.router.on_orders()
async def all_orders(order: Order):
    print(f'Заказ {order.order_id}: {order.status}')
```

### `@fp.router.on_new_order(mapping=None)`

Только новые оплаченные заказы (статус "Оплачен" / "paid" / "відкрито").

```python
@fp.router.on_new_order(mapping=['ключ', 'key'])
async def auto_key(order: Order):
    # сработает только если в описании есть "ключ" или "key"
    await order.answer('Вот твой ключ: ABC-123')
```

### `@fp.router.on_confirmed_orders(mapping=None)`

Только подтверждённые заказы (статус "Закрыт" / "closed" / "закрито").

```python
@fp.router.on_confirmed_orders()
async def confirmed(order: Order):
    await order.answer('Спасибо за подтверждение!')
```

### `@fp.router.on_refunded_orders(mapping=None)`

Только возвраты (статус "Возврат" / "refund" / "повернення").

```python
@fp.router.on_refunded_orders()
async def refund(order: Order):
    print(f'Возврат по заказу {order.order_id}')
```

### `fp.router.order_targets(dict)`

Регистрирует целевые команды для автовыдачи по новым заказам. Ключ — фрагмент описания заказа, значение — функция.

```python
async def sell_guide(order: Order):
    print(f'ЗАКАААЗ')
    await order.answer('Привет, введи свой ник')

fp.router.order_targets({'id: 133': sell_guide})
```

---

## Отзывы

### `@fp.router.on_new_review(stars=None)`

Ловит новые отзывы. Если `stars` указан — только с этим количеством звёзд.

```python
@fp.router.on_new_review(stars=5)
async def good_review(review: CurReview):
    await review.answer('Спасибо!')

@fp.router.on_new_review(stars=1)
async def bad_review(review: CurReview):
    await review.message_author('Давай решим проблему')
```

Можно вешать несколько декораторов на одну функцию:

```python
@fp.router.on_new_review(stars=1)
@fp.router.on_new_review(stars=2)
@fp.router.on_new_review(stars=3)
async def handle_bad(review: CurReview):
    print(f'Плохой отзыв: {review.stars} звезд')
```

---

## Категории (мониторинг цен)

### `@fp.router.on_lot_category()`

Следит за изменениями цен в категориях обычных лотов. Срабатывает когда кто-то меняет цену или появляется новый топ-1. Игнорит твои собственные лоты.

```python
@fp.router.on_lot_category()
async def lot_changed(lot: CategoryLastLot):
    print(f'Новая цена в категории {lot.category_id}: {lot.price}')
```

### `@fp.router.on_chip_category()`

То же самое но для чипсов (короткие лоты под валюты).

```python
@fp.router.on_chip_category()
async def chip_changed(lot: CategoryLastLot):
    print(f'Чипсы: новая цена {lot.price}, лот {lot.offer_id}')
```

---

## Системные хендлеры

### `@fp.router.on_startup()`

Срабатывает один раз при запуске polling, после прогрева кеша.

```python
@fp.router.on_startup()
async def startup():
    print('Бот запущен!')
```

### `@fp.router.on_flood()`

Срабатывает когда FunPay присылает 429 (флуд-контроль). В функцию передаётся количество секунд ожидания.

```python
@fp.router.on_flood()
async def flood_handler(seconds):
    print(f'Флуд на {seconds} секунд')
```

### `@fp.router.on_error()`

Ловит ошибки при обработке команд сообщений.

```python
@fp.router.on_error()
async def error_handler(message, error):
    print(f'Ошибка: {error}')
```

---

## Подключение внешних роутеров

### `fp.router.include_router(router)`

Позволяет подключать хендлеры из других роутеров (для плагинов).

```python
other_router = Router()

@other_router.on_message(text='!test')
async def test(message: Message):
    await message.answer('OK')

fp.router.include_router(other_router)
```
