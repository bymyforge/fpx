"""Тесты OrderParser — страница заказа и категория."""
import pytest
from fpx._parsers._orders import OrderParser
from fpx.utils import errors as fpx_err


class TestOrderParser:
    def test_parse_order_page_full(self):
        """Заказ с описанием, чатом и отзывом."""
        html = """
        <html>
          <h1 class="page-header"><span>Заказ #123</span> <span>Оплачен</span></h1>
          <h5>Подробное описание</h5>
          <div>Описание заказа</div>
          <div class="chat-float" data-id="chat-123"></div>
          <div class="review-container" data-rating="5">
            <div class="review-item-text">Отлично!</div>
            <div class="review-item-answer"><div>Спасибо!</div></div>
          </div>
        </html>
        """
        result = OrderParser.parse_order_page(html)
        assert result["desc"] == "Описание заказа"
        assert result["chat_id"] == "chat-123"
        assert result["status"] == "Заказ #123 / Оплачен"
        assert result["review"]["text"] == "Отлично!"
        assert result["review"]["stars"] == 5
        assert result["review"]["answer"] == "Спасибо!"

    def test_parse_order_page_no_review(self):
        """Заказ без отзыва → review пустой."""
        html = """
        <h1 class="page-header"><span>Заказ #456</span></h1>
        <h5>Подробное описание</h5><div>Описание</div>
        <div class="chat-float" data-id="chat-456"></div>
        """
        result = OrderParser.parse_order_page(html)
        assert result["review"] == {"text": "", "stars": 0, "answer": ""}

    def test_parse_order_page_no_header_raises(self):
        """Нет заголовка h1 → FpxNullDataError."""
        with pytest.raises(fpx_err.FpxNullDataError):
            OrderParser.parse_order_page("<html><body>Пусто</body></html>")

    def test_parse_category_page_with_filters(self):
        """Категория с фильтрами: находит самый дешёвый лот по каждому фильтру."""
        html = """
        <div class="lot-field-radio-box">
          <button value="Все">Все</button>
          <button value="Фильтр1">Ф1</button>
        </div>
        <a class="tc-item" href="/lots/offers?id=111" data-f-1="фильтр1">
          <div class="tc-price" data-s="50.0">50 ₽</div>
          <span class="pseudo-a">Продавец1</span>
        </a>
        <a class="tc-item" href="/lots/offers?id=222" data-f-1="фильтр1">
          <div class="tc-price" data-s="45.0">45 ₽</div>
          <span class="pseudo-a">Продавец2</span>
        </a>
        """
        result = OrderParser.parse_category_page(html)
        assert len(result) == 1
        assert result[0]["filtration"] == "фильтр1"
        assert result[0]["price"] == 45.0
        assert result[0]["offer_id"] == "222"
        assert result[0]["owner_username"] == "Продавец2"

    def test_parse_category_page_no_filters(self):
        """Категория без фильтров: берёт первый лот."""
        html = """
        <a class="tc-item" href="/lots/offers?id=333">
          <div class="tc-price" data-s="99.0">99 ₽</div>
          <span class="pseudo-a">Продавец</span>
        </a>
        """
        result = OrderParser.parse_category_page(html)
        assert len(result) == 1
        assert result[0]["filtration"] == "все"
        assert result[0]["price"] == 99.0

    def test_parse_category_page_empty(self):
        """Пустая категория → пустой список."""
        assert OrderParser.parse_category_page("<html><body>Нет лотов</body></html>") == []
