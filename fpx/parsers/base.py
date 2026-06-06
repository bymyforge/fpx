import re
from bs4 import BeautifulSoup

class BaseParser:
    @staticmethod
    def _safe_parse_links(html_content: str, pattern: str):
        '''Fallback метод'''
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.find_all('a', href=re.compile(pattern))

    @staticmethod
    def clean_text(element) -> str:
        '''Безопасный сбор текста, если элемент не найден, вернет пустую строку'''
        return element.text.strip() if element else ''