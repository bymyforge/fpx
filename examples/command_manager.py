import asyncio
from dataclasses import dataclass
from typing import Annotated

from fpx import Dependency, FunPayTools, Message


@dataclass
class UserSetting:
    """Модель конфигурации текущего состояния продавца"""
    is_online: bool
    can_sell: bool
    is_queue: bool

async def get_setting_object(message: Message) -> UserSetting:
    """Функция для получения настроек из БД,
    Замените возвращаемое значение на реальный запрос в базу данных.
    """
    return UserSetting(is_online=True, can_sell=True, is_queue=False)

async def status_command(message: Message, user: Annotated[UserSetting, Dependency(get_setting_object)]):
    """Обработчик команды !status. Выводит текущий статус продавца."""
    online_status = "в" if user.is_online else "не в"
    sell_status = "могу" if user.can_sell else "не могу"
    queue_status = "есть" if user.is_queue else "пустая"
    await message.answer(
        f"Привет! Я сейчас {online_status} сети, "
        f"{sell_status} выдать заказ, очередь: {queue_status}."
    )

async def ping_seller_command(message: Message):
    '''Обработчик команды !ping. Уведомляет продавца о вызове.'''
    print(f'Продавца вызвал пользователь {message.sender}')
    await message.answer('Продавец уведомлен')

async def main():
    # Инициализируем библиотеку
    fp = FunPayTools('gkey', 'YOUR_GOLDEN_SEAL')

    # Регистрируем команды в роутер
    fp.router.message_commands({
        '!status': status_command,
        '!ping': ping_seller_command
    })

    # Запуск пуллинга
    await fp.runner.start_polling(1, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
