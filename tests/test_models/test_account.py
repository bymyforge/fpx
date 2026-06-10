"""Тесты моделей аккаунта."""
import pytest
from fpx.models.account import (
    Balance, Profile, CurReview, UserData, Order, Review
)
from fpx.models.lots import LotInfo
from unittest.mock import AsyncMock, MagicMock


class TestAccountModels:
    def test_balance_model(self):
        bal = Balance(rub=100.0, usd=1.5, eur=0.8)
        assert bal.rub == 100.0
        assert bal.usd == 1.5
        assert bal.eur == 0.8

    def test_order_model(self):
        order = Order(
            order_id="999", client_name="Вася", price=50.0,
            status="paid", name="Товар", chat_id="chat-1"
        )
        assert order.order_id == "999"
        assert order.price == 50.0

    def test_review_model(self):
        rev = Review(text="Круто", stars=5, answer="Спасибо!")
        assert rev.stars == 5
        assert rev.answer == "Спасибо!"

    def test_user_data_model(self):
        ud = UserData(csrf_token="token", user_id="42")
        assert ud.csrf_token == "token"
        assert ud.user_id == "42"

    def test_lot_info_model(self):
        li = LotInfo(name="Товар", id="123")
        assert li.name == "Товар"
        assert li.id == "123"

    def test_profile_model(self):
        p = Profile(category_ids=["1", "2"], lots=[LotInfo("A", "1")], reviews=[])
        assert p.category_ids == ["1", "2"]

    def test_cur_review_model(self):
        cr = CurReview(text="OK", stars=5, author="User", order_id="10")
        assert cr.text == "OK"
        assert cr.stars == 5

    @pytest.mark.asyncio
    async def test_order_answer_with_mock_client(self):
        order = Order(
            order_id="10", order_time="12:00", client_name="Иван",
            name="Товар", chat_id="chat-10"
        )
        mock_client = MagicMock()
        mock_client._account.chat.send_message = AsyncMock(return_value=True)
        order._client = mock_client
        result = await order.answer("Заказ {order_id} готов!")
        assert result is True
        args = mock_client._account.chat.send_message.call_args[0]
        assert args[1] == "Заказ 10 готов!"

    @pytest.mark.asyncio
    async def test_cur_review_answer_with_mock_client(self):
        order = Order(order_id="99", name="Товар", order_time="12:00")
        review = CurReview(text="OK", stars=5, author="User", order_id="99", order=order)
        mock_client = MagicMock()
        mock_client._account.review.review_answer = AsyncMock(return_value=True)
        review._client = mock_client
        result = await review.answer("Спасибо, {author}!")
        assert result is True
        mock_client._account.review.review_answer.assert_awaited_once()
