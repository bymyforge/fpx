class BaseStorage:
    async def set_state(self, chat_id: str | int, state: str | None) -> None:
        '''Задаёт стейт'''
        raise NotImplementedError()

    async def get_state(self, chat_id: str | int) -> str | None:
        '''Находит состояние'''
        raise NotImplementedError()
    
    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        '''Обновляет данные состояния (принимает kwargs)'''
        raise NotImplementedError()

    async def get_data(self, chat_id: str | int) -> dict:
        '''Забирает данные состояния'''
        raise NotImplementedError()

    async def clear_state(self, chat_id: str | int) -> None:
        '''Очищает состояние и данные полностью'''
        raise NotImplementedError()