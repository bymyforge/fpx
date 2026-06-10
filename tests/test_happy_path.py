"""Интеграционный тест «счастливый путь»."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fpx._parsers._chats import ChatParser
from fpx.fsm import MemoryStorage, FSMContext
from fpx.models.chat import Message


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_full_flow(self):
        """Симуляция: парсим чат → создаём FSM → отправляем ответ."""
        html = """
        <a class="contact-item" href="/chat/?node=777" data-node-msg="1">
          <div class="media-user-name">Покупатель</div>
          <div class="contact-item-message">Здравствуйте!</div>
        </a>
        """
        chats = ChatParser.parse_chats_list(html)
        chat = chats[0]
        assert chat.username == "Покупатель"

        storage = MemoryStorage()
        ctx = FSMContext(storage, chat.id)
        await ctx.set_state("dialog")
        await ctx.update_data(step="greeting")
        assert await ctx.get_state() == "dialog"

        msg = Message(
            sender=chat.username, chat_id=chat.id,
            text=chat.last_msg, is_system=False
        )
        mock_client = MagicMock()
        mock_client._account.chat.send_message = AsyncMock(return_value=True)
        msg._client = mock_client
        result = await msg.answer("Добрый день!")
        assert result is True

        data = await ctx.get_data()
        assert data["step"] == "greeting"
