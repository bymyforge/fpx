"""Тесты BaseParser — вспомогательные статические методы."""
import pytest
from bs4 import BeautifulSoup
from fpx._parsers._base import BaseParser


class TestBaseParser:
    def test_clean_text_with_element(self):
        """Если элемент найден — возвращает его текст без пробелов по краям."""
        html = "<div>  Привет мир  </div>"
        soup = BeautifulSoup(html, "html.parser")
        result = BaseParser.clean_text(soup.find("div"))
        assert result == "Привет мир"

    def test_clean_text_with_none(self):
        """Если элемент None — возвращает пустую строку, не падает."""
        assert BaseParser.clean_text(None) == ""

    def test_safe_parse_links(self):
        """Ищет ссылки по регулярному выражению."""
        html = """
        <a href="/chat/?node=123">Чат 1</a>
        <a href="/chat/?node=456">Чат 2</a>
        <a href="/other">Другая</a>
        """
        links = BaseParser._safe_parse_links(html, r"node=\d+")
        assert len(links) == 2
        assert links[0].get("href") == "/chat/?node=123"
