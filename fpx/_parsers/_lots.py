import json
import logging

from bs4 import BeautifulSoup

from fpx.utils import errors as fpx_err
from ._base import BaseParser

logger = logging.getLogger("fpx.lot_parser")


class LotParser(BaseParser):

    @classmethod
    def parse_lot_menu(cls, html_content: str):
        '''Парсит страницу pay.com/lots/.../trade'''
        soup = BeautifulSoup(html_content, 'html.parser')
        button = soup.find('button', class_='js-lot-raise')
        if not button:
            button = soup.find('button', attrs={'data-game': True})
        if button:
            data_game = button.get('data-game')
            if data_game:
                return data_game
            raise fpx_err.FpxParseError('Атрибут data-game не найден внутри кнопки поднятия')
        raise fpx_err.FpxNullDataError('На странице лотов не найдена кнопка для поднятия. Возможно у вас нет созданных лотов в этой категории')

    @classmethod
    def parse_current_lot_menu(cls, html_content):
        ''' https://funpay.com/lots/offer?id=... '''
        result = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        param_items = soup.find_all('div', class_='param-item')
        if not param_items:
            param_items = [h5.find_parent('div') for h5 in soup.find_all('h5') if h5.find_parent('div')]
        if not param_items:
            raise fpx_err.FpxNullDataError('Страница лота не найдена. Возможно, указана инвалидная ссылка или лот был удалён.')
        else:
            descriptions = {}
            for item in param_items:
                try:
                    header_tag = item.find(['h5', 'h4', 'label'])
                    content_tag = item.find('div') or item.find('textarea')
                    if header_tag and content_tag:
                        header = header_tag.get_text(strip=True)
                        text = content_tag.get_text(separator='\n', strip=True)
                        descriptions[header] = text
                except Exception as e:
                    logger.debug(f'При парсинге конкретного объекта произошла ошибка: {e}')
            result['short_desc'] = descriptions.get('Краткое описание') or descriptions.get('Short description') or descriptions.get('Короткий опис')
            result['description'] = descriptions.get('Подробное описание') or descriptions.get('Detailed description') or descriptions.get('Докладний опис')
            option = soup.find('option', value='21') or soup.find('option', attrs={'data-content': True})
            if option:
                inner_html = option.get('data-content')
                if inner_html:
                    inner_soup = BeautifulSoup(inner_html, 'html.parser')
                    price_span = inner_soup.find('span', class_='payment-value')
                    raw_price = price_span.get_text(strip=True) if price_span else inner_soup.get_text(strip=True)
                    raw_price = raw_price.replace(',', '.')
                    cleaned_price = "".join(c for c in raw_price if c.isdigit() or c == '.')
                    try:
                        result['price'] = float(cleaned_price) if cleaned_price else 0.0
                    except ValueError:
                        result['price'] = 0.0
                    return result
            raise fpx_err.FpxNullDataError('Не удалось найти цену в скрытых атрибутах выбора оплаты.')
    
    @classmethod
    def parse_edit_lot_page(cls, html_content):
        ''' https://funpay.com/lots/offerEdit?node=...&offer=... '''
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        hidden_inputs = soup.find_all('input', type='hidden')
        if not hidden_inputs:
            raise fpx_err.FpxNullDataError('Не найдено вводных данных в редакторе лота. Возможно слетела сессия')
        result = {tag.get('name'): tag.get('value', '') for tag in hidden_inputs if tag.get('name')}
        selects = soup.find_all('select')
        if not selects:
            raise fpx_err.FpxNullDataError('Ни одна выборка в редакторе лотов не найдена. Проверьте актуальность сессии')
        for s in selects:
            try:
                name = s.get('name')
                if not name: continue
                selected_option = s.find('option', selected=True)
                if selected_option:
                    result[name] = selected_option.get('value', '')
                else:
                    first_opt = s.find('option')
                    result[name] = first_opt.get('value', '') if first_opt else ''
            except Exception as e:
                logger.debug(f'При парсинге конкретной выборки произошла ошибка: {e}')
        inputs = soup.find_all('input', class_='form-control')
        if not inputs:
            inputs = [i for i in soup.find_all('input') if i.get('name') and i.get('type') in ['text', 'number', None] and i.get('type') != 'hidden']
        if not inputs:
            logger.debug('Ни одно поле для ввода в редакторе лотов не найдено. Возможно всё в порядке')
        else:
            for i in inputs:
                try:
                    name = i.get('name')
                    if name:
                        result[name] = i.get('value', '')
                except Exception as e:
                    logger.debug(f'При парсинге конкретного поля для ввода произошла ошибка: {e}')
        textareas = soup.find_all('textarea')
        if not textareas:
            logger.debug('При парсинге редактора лотов не найдено ни одного текстового поля. Возможно всё в порядке')
        else:
            for t in textareas:
                try:
                    name = t.get('name')
                    if name:
                        result[name] = t.get_text().strip()
                except Exception as e:
                    logger.debug(f'При парсинге конкретного текстового поля произошла ошибка: {e}')
        return result