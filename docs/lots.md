# Лоты и поднятие

Получение информации о лотах и автоподнятие.

---

## LotManager (через account.lot)

### `await fp.account.lot.get_lot_info(lot_id)`

Информация о лоте.

```python
lot = await fp.account.lot.get_lot_info('12345678')
print(lot.short_desc)   # краткое описание
print(lot.description)  # полное описание
print(lot.price)        # цена (float)
```

Возвращает `CurrentLotInfo`.

### `await fp.account.lot.raise_lots()`

Поднимает все твои лоты во всех категориях.

```python
responses = await fp.account.lot.raise_lots()
```

Возвращает список ответов от сервера. Если у тебя нет лотов — кинет `FpxRaisingLotError`.

**Пример автоподнятия:**

```python
import asyncio

async def auto_raise():
    while True:
        try:
            await fp.account.lot.raise_lots()
            print('Лоты подняты')
        except Exception as e:
            print(f'Ошибка: {e}')
        await asyncio.sleep(60 * 30)  # раз в 30 минут

# Запускаем фоном
asyncio.create_task(auto_raise())
await fp.runner.start_polling(3, is_background=True)
await fp.runner.idle()
```

---

## Внутренний метод (для редактора)

### `await fp.account.lot._get_lot_editor_details(lot_id)`

Возвращает технический объект `LotEditor` с полными данными формы редактирования. Используется внутри редактора, самому вызывать не нужно.

Возвращает `LotEditor`:
- `csrf_token`, `form_created_at`, `offer_id`, `node_id`
- `fields` — словарь со всеми полями лота
