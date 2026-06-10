# Редактор лотов

Изменение цен, включение/выключение лотов. Всё через `fp.account.editor`.

---

## FunPayEditor (через account.editor)

### `await fp.account.editor.change_lot_price(lot_id, new_price)`

Меняет цену лота. После изменения делает паузу 0.5 сек и проверяет что цена реально поменялась.

```python
await fp.account.editor.change_lot_price('12345678', '150.50')
```

Цену передавать **строкой**.

Возвращает `True` если цена изменена. Если на сайте цена осталась старой — `FpxLotEditingError`.

**Пример автодемпинга:**

```python
from fpx import CategoryLastLot

MY_LOT_ID = '11223344'

@fp.router.on_lot_category()
async def auto_dump(lot: CategoryLastLot):
    new_price = round(lot.price - 0.1, 2)
    await fp.account.editor.change_lot_price(MY_LOT_ID, str(new_price))
    print(f'Перебил цену до {new_price}')
```

### `await fp.account.editor.toggle_off_lot(lot_id)`

Выключает лот (убирает из поиска).

```python
await fp.account.editor.toggle_off_lot('12345678')
```

### `await fp.account.editor.toggle_on_lot(lot_id)`

Включает лот обратно.

```python
await fp.account.editor.toggle_on_lot('12345678')
```

Обе функции возвращают `True` при успехе. При ошибке — `FpxRequestError`.
