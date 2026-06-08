<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

<h1 align="center">fpx</h1>

<p align="center">
  <strong>fpx</strong> - асинхронный Python-фреймворк и библиотека для упрощения взаимодействия с <a href="https://funpay.com">funpay.com</a>. Моя философия это максимальная простота взаимодействия с кодом, я хочу чтобы разработчик вообще не напрягался насчёт фп когда использовал мой код
</p>

<p align="center">
  <a href="https://github.com/bymyforge/fpx" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="https://fpx.readthedocs.io/ru/latest/" target="_blank">
    <img src="https://img.shields.io/badge/Документация-00b0ff?style=for-the-badge&logo=read-the-docs&logoColor=white" alt="Read the Docs">
  </a>
  <a href="https://t.me/fpx_engine" target="_blank">
    <img src="https://img.shields.io/badge/Телеграм_Чат-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>
  <a href="https://pypi.org/project/fpx-engine/" target="_blank">
    <img src="https://img.shields.io/badge/PyPI-3775A9?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI">
  </a>
</p>

---

Оригинальный сайт не предоставляет публичного API для разработчиков. Наш проект нацелен на то, чтобы облегчить написание различных автоматизаций. Используя **fpx**, разработчик может полностью сфокусироваться на логике своего приложения, не отвлекаясь на написание парсеров и ручную сборку HTTP-запросов, кеширование. Фреймворк делает всю грязную работу под капотом.

## ✨ Особенности
* **Два в одном:** работает и как полноценный событийный фреймворк на хэндлерах и декораторах, и как гибкая библиотека для точечных запросов.
* **Полная асинхронность:** построен на базе `httpx`
* **Автоматизация из коробки:** встроенный движок для отслеживания событий.

## Установка    
Установка библиотеки:      
```
pip install fpx-engine  
``` 
Обновление библиотеки:  
```
pip install -U fpx-engine
```

## 🚀 Пример использования

Получение нового сообщения и автоматический ответ на него:

```python
import asyncio
from fpx import FunPayTools, Message

async def main():
    # инициализируем аккаунт
    fp = FunPayTools('gkey')
    # ловим сообщение
    @fp.router.on_message()
    async def answer_message(message: Message):
        # отвечаем на сообщение
        await message.answer('Привет')
    #запускаем приём событий
    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```
## ⚠️ Статус проекта
Проект находится в процессе активной разработки. Будем рады любой обратной связи!
Если вы обнаружили баг, у вас есть предложения по улучшению или вопросы по работе фреймворка, просьба сообщать в Telegram: @sanyalca.
