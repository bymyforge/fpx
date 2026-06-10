"""Тесты FSM (Finite State Machine)."""
import pytest
from fpx.fsm import MemoryStorage, FSMContext


class TestMemoryStorage:
    @pytest.mark.asyncio
    async def test_set_and_get_state(self):
        storage = MemoryStorage()
        await storage.set_state("chat_1", "waiting_name")
        assert await storage.get_state("chat_1") == "waiting_name"

    @pytest.mark.asyncio
    async def test_get_state_empty(self):
        storage = MemoryStorage()
        assert await storage.get_state("unknown") is None

    @pytest.mark.asyncio
    async def test_update_and_get_data(self):
        storage = MemoryStorage()
        await storage.update_data("chat_1", name="Иван")
        await storage.update_data("chat_1", age="25")
        data = await storage.get_data("chat_1")
        assert data == {"name": "Иван", "age": "25"}

    @pytest.mark.asyncio
    async def test_get_data_empty(self):
        storage = MemoryStorage()
        assert await storage.get_data("unknown") == {}

    @pytest.mark.asyncio
    async def test_clear_state(self):
        storage = MemoryStorage()
        await storage.set_state("chat_1", "state")
        await storage.update_data("chat_1", key="val")
        await storage.clear_state("chat_1")
        assert await storage.get_state("chat_1") is None
        assert await storage.get_data("chat_1") == {}

    @pytest.mark.asyncio
    async def test_overwrite_state(self):
        storage = MemoryStorage()
        await storage.set_state("chat_1", "state1")
        await storage.set_state("chat_1", "state2")
        assert await storage.get_state("chat_1") == "state2"


class TestFSMContext:
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        storage = MemoryStorage()
        ctx = FSMContext(storage, "user_42")
        await ctx.set_state("ordering")
        assert await ctx.get_state() == "ordering"
        await ctx.update_data(product="Телефон", qty="2")
        data = await ctx.get_data()
        assert data["product"] == "Телефон"
        assert data["qty"] == "2"
        await ctx.clear_state()
        assert await ctx.get_state() is None
        assert await ctx.get_data() == {}

    @pytest.mark.asyncio
    async def test_multiple_chats_isolated(self):
        storage = MemoryStorage()
        ctx1 = FSMContext(storage, "chat_1")
        ctx2 = FSMContext(storage, "chat_2")
        await ctx1.set_state("A")
        await ctx2.set_state("B")
        assert await ctx1.get_state() == "A"
        assert await ctx2.get_state() == "B"
