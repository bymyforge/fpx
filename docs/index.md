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

## Установка

```bash
pip install fpx-engine
```

Обновление:

```bash
pip install -U fpx-engine
```

## Минимальный пример

Получение нового сообщения и автоматический ответ на него:

```python
import asyncio
from fpx import FunPayTools, Message

async def main():
    fp = FunPayTools('gkey')

    @fp.router.on_message()
    async def answer_message(message: Message):
        await message.answer('Привет')

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```

## Статус проекта

Проект находится в процессе активной разработки. Будем рады любой обратной связи!
Если вы обнаружили баг, у вас есть предложения по улучшению или вопросы по работе фреймворка, просьба сообщать в Telegram: @sanyalca.
