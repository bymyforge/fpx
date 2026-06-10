"""Тесты Router — декораторы, регистрация хендлеров, подключение под-роутеров."""
import pytest
from fpx.classes.runner.subclasses.router import Router


class TestRouter:
    def test_router_creation(self):
        router = Router()
        assert router is not None
        assert isinstance(router._handlers, dict)
        assert "message" in router._handlers
        assert "startup" in router._handlers

    def test_on_message_decorator(self):
        router = Router()
        @router.on_message()
        async def handler(msg): pass
        assert len(router._handlers["message"]) == 1
        assert router._handlers["message"][0]["function"] == handler

    def test_on_message_with_filter(self):
        router = Router()
        @router.on_message(text="!start")
        async def handler(msg): pass
        assert router._handlers["message"][0]["filter_text"] == "!start"

    def test_on_message_with_mapping(self):
        router = Router()
        @router.on_message(mapping={"Привет": "Здравствуй!"})
        async def handler(msg): pass
        assert router._handlers["message"][0]["mapping"] == {"Привет": "Здравствуй!"}

    def test_on_new_order_decorator(self):
        router = Router()
        @router.on_new_order()
        async def handler(order): pass
        assert len(router._handlers["new_order"]) == 1
        assert router._handlers["new_order"][0]["function"] == handler

    def test_on_confirmed_orders_decorator(self):
        router = Router()
        @router.on_confirmed_orders()
        async def handler(order): pass
        assert len(router._handlers["confirmed_order"]) == 1

    def test_on_refunded_orders_decorator(self):
        router = Router()
        @router.on_refunded_orders()
        async def handler(order): pass
        assert len(router._handlers["refund"]) == 1

    def test_on_orders_decorator(self):
        router = Router()
        @router.on_orders()
        async def handler(order): pass
        assert len(router._handlers["order"]) == 1

    def test_on_new_review_decorator(self):
        router = Router()
        @router.on_new_review(stars=5)
        async def handler(review): pass
        assert len(router._handlers["review"]) == 1
        assert router._handlers["review"][0]["stars"] == 5

    def test_on_lot_category_decorator(self):
        router = Router()
        @router.on_lot_category()
        async def handler(lot): pass
        assert len(router._handlers["lot_category"]) == 1
        assert router._handlers["lot_category"][0] == handler

    def test_on_chip_category_decorator(self):
        router = Router()
        @router.on_chip_category()
        async def handler(lot): pass
        assert len(router._handlers["chip_category"]) == 1

    def test_on_startup_decorator(self):
        router = Router()
        @router.on_startup()
        async def handler(): pass
        assert len(router._handlers["startup"]) == 1
        assert router._handlers["startup"][0] == handler

    def test_on_flood_decorator(self):
        router = Router()
        @router.on_flood()
        async def handler(): pass
        assert len(router._handlers["flood"]) == 1

    def test_on_error_decorator(self):
        router = Router()
        @router.on_error()
        async def handler(e): pass
        assert len(router._handlers["error"]) == 1
        assert router._handlers["error"][0] == handler

    def test_message_commands(self):
        router = Router()
        router.message_commands({"Привет": "Здравствуй!", "Цена": "100₽"})
        assert len(router._handlers["commands"]) == 1
        assert router._handlers["commands"][0]["command"] == {"Привет": "Здравствуй!", "Цена": "100₽"}

    def test_order_targets(self):
        router = Router()
        router.order_targets({"моя метка": lambda o: o})
        assert len(router._handlers["order_command"]) == 1

    def test_include_router(self):
        main = Router()
        sub = Router()
        @sub.on_message()
        async def sub_handler(msg): pass
        @sub.on_new_order()
        async def sub_order(o): pass
        main.include_router(sub)
        assert len(main._handlers["message"]) == 1
        assert len(main._handlers["new_order"]) == 1

    def test_multiple_decorators_same_type(self):
        router = Router()
        @router.on_message()
        async def h1(msg): pass
        @router.on_message()
        async def h2(msg): pass
        assert len(router._handlers["message"]) == 2
