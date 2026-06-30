# fpx-engine

**fpx** — асинхронный Python-фреймворк и библиотека для упрощения взаимодействия с [funpay.com](https://funpay.com). Моя философия это максимальная простота, я хочу чтобы разработчик вообще не напрягался насчёт фп когда использовал мой код.

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/bymyforge/fpx)
[![Документация](https://img.shields.io/badge/Документация-00b0ff?style=for-the-badge&logo=read-the-docs&logoColor=white)](https://fpx.readthedocs.io/ru/latest/)
[![Телеграм Чат](https://img.shields.io/badge/Телеграм_Чат-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/fpx_engine)
[![PyPI](https://img.shields.io/badge/PyPI-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/fpx-engine/)

---

Оригинальный сайт не предоставляет публичного API для разработчиков. Наш проект нацелен на то, чтобы облегчить написание различных автоматизаций. Используя **fpx**, разработчик может полностью сфокусироваться на логике своего приложения, не отвлекаясь на написание парсеров и ручную сборку HTTP-запросов, кеширование. Фреймворк делает всю грязную работу под капотом.

## Что умеет

- **Два в одном**: работает и как полноценный событийный фреймворк на хэндлерах и декораторах, и как гибкая библиотека для точечных запросов.
- **Полная асинхронность**: построен на базе `httpx`.
- **Автоматизация из коробки**: встроенный движок для отслеживания событий.
- **Два стиля взаимодействия**: простой (всё через один объект) и продвинутый (раздельные `account`/`runner`/`router`) — выбирай по вкусу, см. ниже.

## Установка

```bash
pip install fpx-engine
```

Обновление:

```bash
pip install -U fpx-engine
```

## Минимальный пример

Получение нового сообщения и автоматический ответ на него. `golden_key` и `golden_seal` — это куки твоего аккаунта на funpay.com (как их достать — в [быстром старте](quickstart.md)):

```python
import asyncio
from fpx import FunPayTools, types

async def main():
    fp = FunPayTools('golden_key', 'golden_seal')

    @fp.router.on_message()
    async def answer_message(message: types.Message):
        await message.answer('Привет')

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```

## Два варианта взаимодействия с библиотекой

В fpx не нужно самому создавать `Account`, `Runner` или менеджеры - всё уже собрано за тебя внутри `FunPayTools`. Есть два равноправных способа этим пользоваться: простой и продвинутый. Выбери удобный - итоговая логика бота не меняется.

### Простой вариант - всё через `FunPayTools`

Один объект `fp = FunPayTools(...)` даёт доступ ко всему: `fp.router` для хендлеров, `fp.account` для прямых запросов, `fp.runner` для управления поллингом.

```python
from fpx import FunPayTools, types

fp = FunPayTools('golden_key', 'golden_seal')

@fp.router.on_message()
async def new_msg(message: types.Message):
    print(f'Сообщение: {message}')
```

Подходит для небольших скриптов и быстрого старта - меньше сущностей держать в голове.

### Продвинутый вариант - раздельные объекты

Если проект растёт и хочется разнести логику по модулям, можно явно вытащить нужные объекты из `fp` и работать с ними напрямую, без постоянной оглядки на `fp.`:

```python
from fpx import FunPayTools, types

fp = FunPayTools('golden_key', 'golden_seal')

account = fp.account
runner = fp.runner
router = runner.router

@router.on_message()
async def new_msg(message: types.Message):
    print(f'Сообщение: {message}')
```

`account`, `runner` и `router` - это те же самые объекты, что и `fp.account`, `fp.runner`, `fp.router`, просто извлечённые в отдельные переменные. Удобно когда `account` нужен в одном модуле, а хендлеры регистрируются в другом.

### Доступ к функциональности: два пути

Независимо от выбранного стиля, методы библиотеки доступны двумя способами:

**1. Через готовые менеджеры на `account`** (самый простой путь - ничего создавать не нужно):

```python
chats = await fp.account.chat.get_chats()
balance = await fp.account.profile.get_balance()
await fp.account.order.refund_order('ABC123')
```

**2. Через отдельный импорт менеджера из `fpx.services`**, если хочешь явно объявить нужный менеджер как отдельную переменную (например, чтобы передавать его между функциями):

```python
from fpx.services import OrderManager, ChatManager

order = OrderManager(fp.account)
chat = ChatManager(fp.account)

await order.refund_order('ABC123')
await chat.get_chats()
```

Важно: классы менеджеров (`OrderManager`, `ChatManager`, `ProfileManager` и т.д.) **не создают свою собственную логику** - они всегда принимают уже существующий `account` (например `fp.account`) и просто дают к нему ещё один способ доступа. Самостоятельно объявлять `Account`, `Runner` или модели данных не нужно — это сделает за тебя `FunPayTools`.

Полный список менеджеров и их методов - в разделах [Чаты](chat.md), [Заказы](orders.md), [Отзывы](review.md), [Профиль](profile.md), [Лоты](lots.md), [Редактор](editor.md), [Категории](category.md).

### Разделение хендлеров по файлам через `Router`

Хендлеры не обязательно регистрировать в одном файле - в любом модуле можно создать свой `Router` и подключить его к главному:

```python
# handlers/messages.py
from fpx import Router, types

router = Router()

@router.on_message(text='!привет')
async def hello(message: types.Message):
    await message.answer('Привет!')
```

```python
# main.py
import asyncio
from fpx import FunPayTools
from handlers.messages import router as messages_router

async def main():
    fp = FunPayTools('golden_key', 'golden_seal')

    # простой вариант:
    fp.router.include_router(messages_router)

    # или (если используешь продвинутый вариант с отдельным router = fp.router):
    # router.include_router(messages_router)

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```

Это работает одинаково для обоих стилей — `include_router` есть у любого объекта `Router`, будь то `fp.router` или отдельная переменная `router`, полученная через `runner.router`.

## Статус проекта

Проект находится в процессе активной разработки. Будем рады любой обратной связи!
Если вы обнаружили баг, у вас есть предложения по улучшению или вопросы по работе фреймворка, просьба сообщать в Telegram: @sanyalca.
