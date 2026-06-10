# Мониторинг категорий

Отслеживание цен конкурентов в категориях.

---

## Хендлеры

### `@fp.router.on_lot_category()`

Следит за обычными лотами. Срабатывает когда меняется цена или топ-1 в отслеживаемых категориях. Твои собственные лоты игнорируются.

```python
@fp.router.on_lot_category()
async def lot_changed(lot: CategoryLastLot):
    print(f'Конкурент {lot.owner_username} перебил цену до {lot.price}')
```

### `@fp.router.on_chip_category()`

То же самое для чипсов (игровая валюта).

```python
@fp.router.on_chip_category()
async def chip_changed(lot: CategoryLastLot):
    print(f'Чипсы: {lot.offer_id} = {lot.price}')
```

---

## Запуск мониторинга

Чтобы хендлеры срабатывали, нужно передать `watch_lots` и/или `watch_chips` в `start_polling`:

```python
await fp.runner.start_polling(
    3,
    is_background=True,
    watch_lots=[1316, 99],    # ID категорий лотов
    watch_chips=[55]          # ID категорий чипсов
)
```

---

## Объект CategoryLastLot

| Поле | Тип | Описание |
|------|-----|----------|
| `category_id` | `str` | ID категории |
| `filtration` | `str` | Название фильтра |
| `price` | `float` | Цена лота |
| `offer_id` | `str` | ID лота |
| `owner_username` | `str` | Ник продавца |

---

## CategoryManager (через account.category)

### `await fp.account.category.get_lot_category_last_lot(category_id)`

Возвращает самый дешёвый лот по каждому фильтру в категории.

```python
lots = await fp.account.category.get_lot_category_last_lot(1316)
for lot in lots:
    print(f'{lot.filtration}: {lot.price} у {lot.owner_username}')
```

Возвращает `list[CategoryLastLot]`.

### `await fp.account.category.get_chip_category_last_lot(category_id)`

То же самое для чипсов.

```python
lots = await fp.account.category.get_chip_category_last_lot(55)
```
