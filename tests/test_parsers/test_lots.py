"""Тесты LotParser — данные лотов, редактор, поднятие."""
import pytest
from fpx._parsers._lots import LotParser
from fpx.utils import errors as fpx_err


class TestLotParser:
    def test_parse_lot_menu_success(self):
        """Кнопка поднятия с data-game → возвращает ID игры."""
        html = """<button class="js-lot-raise" data-game="42">Поднять</button>"""
        assert LotParser.parse_lot_menu(html) == "42"

    def test_parse_lot_menu_fallback_button(self):
        """Fallback: кнопка без класса, но с data-game."""
        html = """<button data-game="99">Поднять</button>"""
        assert LotParser.parse_lot_menu(html) == "99"

    def test_parse_lot_menu_no_button_raises(self):
        """Нет кнопки → FpxNullDataError."""
        with pytest.raises(fpx_err.FpxNullDataError):
            LotParser.parse_lot_menu("<html><body>Нет кнопки</body></html>")

    def test_parse_current_lot_menu_success(self):
        """Парсинг лота: цена, краткое и подробное описание."""
        html = """
        <html>
          <div class="param-item"><h5>Краткое описание</h5><div>Кратко</div></div>
          <div class="param-item"><h5>Подробное описание</h5><div>Подробно</div></div>
          <option value="21" data-content='<span class="payment-value">100,50</span>'></option>
        </html>
        """
        result = LotParser.parse_current_lot_menu(html)
        assert result["short_desc"] == "Кратко"
        assert result["description"] == "Подробно"
        assert result["price"] == 100.50

    def test_parse_current_lot_menu_no_price_raises(self):
        """Нет опции с ценой → FpxNullDataError."""
        html = """
        <div class="param-item"><h5>Краткое описание</h5><div>Кратко</div></div>
        """
        with pytest.raises(fpx_err.FpxNullDataError):
            LotParser.parse_current_lot_menu(html)

    def test_parse_edit_lot_page_success(self):
        """Парсинг редактора: скрытые поля формы."""
        html = """
        <input type="hidden" name="csrf_token" value="abc123">
        <input type="hidden" name="offer_id" value="999">
        <select><option value="1">Опция</option></select>
        """
        result = LotParser.parse_edit_lot_page(html)
        assert result["csrf_token"] == "abc123"
        assert result["offer_id"] == "999"

    def test_parse_edit_lot_page_no_inputs_raises(self):
        """Нет скрытых input → FpxNullDataError."""
        with pytest.raises(fpx_err.FpxNullDataError):
            LotParser.parse_edit_lot_page("<html><body>Пусто</body></html>")

    def test_parse_edit_lot_page_no_selects_raises(self):
        """Есть inputs, но нет select → тоже ошибка."""
        html = """<input type="hidden" name="x" value="y">"""
        with pytest.raises(fpx_err.FpxNullDataError):
            LotParser.parse_edit_lot_page(html)
