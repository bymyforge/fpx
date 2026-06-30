
# Быстрый старт

Разберём как поднять первого бота на fpx-engine.

---

## 1. Получение golden_key

Для работы нужен твой `golden_key` и `golden_seal` - они берутся из куков браузера.

1. Открываешь [funpay.com](https://funpay.com), заходишь в аккаунт.
2. F12 → Application → Cookies → `https://funpay.com`
3. Ищешь куку `golden_key`, `golden_seal` и копируешь её значение.

⚠️ **НИКОГДА** не выкладывай куки в открытый доступ. Это полный доступ к твоему аккаунту.

---

Требуется Python 3.10+.

---

## 3. Первый запуск

Создай файл `main.py`:

```python
import asyncio
from fpx import FunPayTools, types

async def main():
    fp = FunPayTools('ВАШ_GOLDEN_KEY', 'ВАШ_GOLDEN_SEAL')

    @fp.router.on_message()
    async def echo(message: types.Message):
        await message.answer(f'Ты написал: {message.text}')

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```

Запуск:

```bash
python main.py
```

Попробуй написать своему боту с другого аккаунта — он ответит.

> 💡 В примере выше использован простой стиль (всё через `fp`). Есть ещё продвинутый стиль с раздельными `account`/`runner`/`router` — оба способа равноправны, выбирай по вкусу. Подробнее - на [главной странице](index.md#два-варианта-взаимодействия-с-библиотекой).

---

## 4. Следующие шаги

- [Роутер и хендлеры](router.md) - все декораторы и события
- [Чаты](chat.md) - работа с сообщениями
- [Заказы](orders.md) - автовыдача и отслеживание
- [Машина состояний](fsm.md) - пошаговые диалоги
