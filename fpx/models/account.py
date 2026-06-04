from dataclasses import dataclass, field
from typing import Optional, Any

from fpx.utils import errors as fpx_err

@dataclass
class Balance:
    rub: float=0.0
    usd: float=0.0
    eur: float=0.0

@dataclass
class Profile:
    category_ids: list
    lots: list[LotInfo] = field(default_factory=list)
    reviews: list[CurReview] = field(default_factory=list)

@dataclass
class CurReview:
    text: str
    stars: int
    author: str
    order_id: str
    order: Optional[Order] = None
    _client: Any = field(init=False, repr=False, default=None)

    async def answer(self, answer_text: str) -> bool:
        '''Ответить на отзыв'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurReview не привязан к клиенту fpx')
        formatted_reply = answer_text.format(
            author=self.author,
            order_id=self.order_id,
            order_name=self.order.name,
            order_time=self.order.order_time,
            stars=self.stars
        )
        return await self._client._account.review.review_answer(self.order_id, formatted_reply)
    
    async def message_author(self, message_text: str) -> bool:
        '''Ответить на отзыв в чате'''
        if not self._client:
            raise fpx_err.FpxCriticalRunnerError('Объект CurReview не привязан к клиенту fpx')
        formatter_reply = message_text.format(
            author=self.author,
            order_id=self.order_id,
            order_name=self.order.name,
            order_time=self.order.order_time,
            stars=self.stars
        )
        #добавить ещё ревью тайм
        return await self._client._account.chat.send_message(self.order.chat_node_id, formatter_reply)

@dataclass
class UserData:
    csrf_token: str
    user_id: str

@dataclass
class Order:
    order_id: Optional[str] = None
    chat_id: Optional[str] = None
    order_time: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    review: Optional[dict] = None
    _client: Any = field(init=False, repr=False, default=None)

    async def answer(self, answer_text: str) -> bool:
        '''Ответить в этот же чат'''
        if not self._client:
            raise fpx_err.FpxClientNotAttachedError('Объект Order не привязан к клиенту fpx')
        formatted_reply = answer_text.format(
                            order_id=self.order_id,
                            order_time=self.order_time,
                            client_name=self.client_name,
                            order_name=self.name
                        )
        return await self._client._account.chat.send_message(self.chat_id, formatted_reply)

@dataclass
class Review:
    text: str
    stars: int
    answer: str