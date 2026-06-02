<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

<h1 align="center">fpx</h1>

<p align="center">
  <strong>fpx</strong> - асинхронный Python-фреймворк и библиотека для упрощения взаимодействия с <a href="https://funpay.com">funpay.com</a>.
</p>

<p align="center">
  <a href="https://github.com/bymyforge/fpx" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="https://t.me/fpx_engine" target="_blank">
    <img src="https://img.shields.io/badge/Telegram_Канал-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
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
from fpx import FunPayTools

async def main():
    # Инициализируем аккаунт (замените 'gkey' на golden_key вашего аккаунта)
    fp = FunPayTools('gkey')

    # Ловим новое сообщение
    @fp.handler.on_message()
    async def get_message(message):
        print(f'Пришло сообщение: {message.text} от {message.sender}')
        
        # Отвечаем в чат
        new_message = await fp.account.chat.send_message(message.chat_id, 'Привет, я на связи!')
        if new_message:
            print('Успешно ответил на сообщение')
        else:
            print('Не удалось отправить сообщение!')

    # Запускаем слушатель событий в фоновом режиме (опрос каждые 3 секунды)
    await fp.runner.runner_polling(3, is_background=True)
    
    # Зацикливаем программу, чтобы фоновые функции не останавливались
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
```
## ⚠️ Статус проекта
Проект находится в процессе активной разработки. Будем рады любой обратной связи!
Если вы обнаружили баг, у вас есть предложения по улучшению или вопросы по работе фреймворка, просьба сообщать в Telegram: @sanyalca.
