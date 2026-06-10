class BaseStorage:
    async def set_state(self, chat_id: str | int, state: str | None) -> None:
        '''Задаёт стейт'''
        pass

    async def get_state(self, chat_id: str | int) -> str | None:
        '''Находит состояние'''
        pass
    
    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        '''Обновляет данные состояния (принимает kwargs)'''
        pass

    async def get_data(self, chat_id: str | int) -> dict:
        '''Забирает данные состояния'''
        pass

    async def clear_state(self, chat_id: str | int) -> None:
        '''Очищает состояние и данные полностью'''
        pass