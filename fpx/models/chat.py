from dataclasses import dataclass, field
from typing import Any

from fpx.utils import errors as fpx_err

@dataclass
class Chat:
    '''
    id: Chat id (node)
    username: Client nickname
    last_msg: Last message in chat
    date: last message date
    link: full chat link (https://funpay.com/chat/?node=id)
    is_unread: Readed or not
    '''
    id: str
    node_msg_id: int
    username: str
    last_msg: str
    date: str
    link: str
    is_unread: bool

@dataclass
class ChatData:
    node_name: str
    csrf_token: str
    user_id: str
    last_message: list

@dataclass
class Message:
    sender: str
    chat_id: str
    text: str
    is_system: bool
    _client: Any = field(init=False, repr=False, default=None)

    async def answer(self, answer_text: str) -> bool:
        '''Ответить в этот же чат'''
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Message не привязан к клиенту fpx')
        formatted_reply = answer_text.format(
                            sender=self.sender,
                            chat_id=self.chat_id,
                            text=self.text
                        )
        return await self._client._account.chat.send_message(self.chat_id, formatted_reply)

    async def set_state(self, state: str ):
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Message не привязан к клиенту fpx')
        return await self._client.storage.set_state(self.chat_id, state)
        
    async def clear_state(self):
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Message не привязан к клиенту fpx')
        return await self._client.storage.clear_state(self.chat_id)

    async def update_data(self, data_key: str, data_value: str):
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Message не привязан к клиенту fpx')
        return await self._client.storage.update_data(self.chat_id, data_key, data_value)

    async def get_data(self):
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Message не привязан к клиенту fpx')
        return await self._client.storage.get_data(self.chat_id)