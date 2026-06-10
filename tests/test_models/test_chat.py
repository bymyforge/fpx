"""Тесты моделей чатов."""
import pytest
from fpx.models.chat import Chat, ChatData, Message
from fpx.utils import errors as fpx_err
from unittest.mock import AsyncMock, MagicMock


class TestChatModels:
    def test_chat_model(self):
        chat = Chat(
            id="123", node_msg_id=1, username="User",
            last_msg="Hi", date="10:00", link="/chat/?node=123", is_unread=True
        )
        assert chat.id == "123"
        assert chat.is_unread is True

    def test_chat_data_model(self):
        cd = ChatData(node_name="users-1-2", csrf_token="abc", user_id="1", last_message=[])
        assert cd.node_name == "users-1-2"

    def test_message_answer_without_client_raises(self):
        msg = Message(sender="User", chat_id="123", text="Hello", is_system=False)
        with pytest.raises(fpx_err.FpxClientNotAttachedError):
            import asyncio
            asyncio.run(msg.answer("Привет"))

    @pytest.mark.asyncio
    async def test_message_answer_with_mock_client(self):
        msg = Message(sender="User", chat_id="123", text="Hello", is_system=False)
        mock_client = MagicMock()
        mock_client._account.chat.send_message = AsyncMock(return_value=True)
        msg._client = mock_client
        result = await msg.answer("Ответ")
        assert result is True
        mock_client._account.chat.send_message.assert_awaited_once_with("123", "Ответ")
