import json
import logging

from bs4 import BeautifulSoup

from fpx.utils import errors as fpx_err
from .base import BaseParser

logger = logging.getLogger("fpx.order_parser")


class OrderParser(BaseParser):
    @classmethod
    def parse_order_page(cls, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        result['review'] = {}
        try:
            languages = ['подробное описание', 'detailed description', 'докладний опис']
            desc_h5 = soup.find('h5', string=lambda text: text and any(lang in text.lower() for lang in languages))
            if desc_h5:
                desc_div = desc_h5.find_next(['div', 'p', 'span'])
                if desc_div:
                    result['desc'] = desc_div.get_text(separator="\n").strip()
            chat_link = soup.select_one('div.chat-float[data-id]')
            if chat_link:
                result['chat_id'] = chat_link.get('data-id', '')
            else:
                chat_link = soup.select_one('div[data-id][data-name*="users-"]')
                result['chat_id'] = chat_link.get('data-id', '') if chat_link else None
            header = soup.find('h1', class_='page-header') or soup.find('h1')
            if not header:
                raise fpx_err.FpxNullDataError('Страница заказа не найдена, возможно, указан неверный ID или слетела сессия.')
            spans = header.find_all('span')
            if spans:
                result['status'] = " / ".join([span.get_text(strip=True) for span in spans])
            else:
                full_header_text = header.get_text(separator=' ', strip=True)
                order_langs = ['заказ', 'order', 'замовлення']
                if any(word in full_header_text.lower() for word in order_langs):
                    parts = full_header_text.split()
                    idx = next((i for i, part in enumerate(parts) if '#' in part), -1)
                    if idx != -1 and idx + 1 < len(parts):
                        result['status'] = " ".join(parts[idx + 1:])
                    else:
                        result['status'] = parts[-1] if parts else 'Оплачен'
                else:
                    result['status'] = full_header_text or 'Оплачен'
                
            review_container = soup.find('div', class_='review-container')
            if review_container:
                try:
                    text_tag = review_container.find('div', class_='review-item-text') or review_container.find('div')
                    result['review']['text'] = text_tag.get_text(strip=True) if text_tag else ''
                    raw_stars = review_container.get('data-rating', '0')
                    result['review']['stars'] = int(raw_stars) if raw_stars.isdigit() else 0
                    answer_div = review_container.find('div', class_='review-item-answer')
                    if answer_div:
                        text_container = answer_div.find('div') or answer_div
                        result['review']['answer'] = text_container.get_text('\n', strip=True)
                    else:
                        all_divs = review_container.find_all('div', recursive=False)
                        if len(all_divs) > 1:
                            result['review']['answer'] = all_divs[-1].get_text('\n', strip=True)
                        else:
                            result['review']['answer'] = ''
                except Exception as e:
                    logger.debug(f'Ошибка парсинга деталей существующего отзыва: {e}')
                    result['review'].update({'text': '', 'stars': 0, 'answer': ''})
            else:
                result['review'] = {'text': '', 'stars': 0, 'answer': ''}
        except fpx_err.FpxNullDataError:
            raise
        except fpx_err.FpxParseError:
            raise
        except Exception as e:
            raise fpx_err.FpxParseError(f'Ошибка парсинга страницы заказа: {e}')
        return result

    @classmethod
    def parse_category_page(cls, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        lowcoasters = {}
        buttons = soup.select('div.lot-field-radio-box button')
        if not buttons:
            buttons = [btn for btn in soup.find_all('button') if btn.get('value') and btn.get('value') != 'Все']
        filters = [btn.get('value').strip().lower() for btn in buttons if btn.get('value') and btn.get('value') != 'Все']
        lots = soup.select('a.tc-item:not(.offer-promo)')
        if not lots:
            lots = [
                a for a in soup.find_all('a', href=lambda h: h and '/lots/offers/' in h)
                if 'promo' not in "".join(a.get('class', [])).lower()
            ]
        if not lots:
            logger.debug('В категории не найдено лотов, возможно их просто нет или страница сломалась')
            return []
        if not filters:
            try:
                lot = lots[0]
                price_div = lot.find('div', class_='tc-price') or lot.find('div', attrs={'data-s': True})
                lot_price = float(price_div.get('data-s', 0)) if price_div else 0.0
                if lot_price in(1.0, 0.0) or not price_div:
                    target_div = price_div or lot
                    raw_text = target_div.get_text(strip=True).replace(',', '.')
                    cleaned = "".join(c for c in raw_text if c.isdigit() or c == '.')
                    lot_price = float(cleaned) if cleaned else 0.0
                username_el = lot.find('span', class_='pseudo-a') or lot.select_one('.media-user-name span')
                owner_username = username_el.get_text(strip=True) if username_el else "Unknown"
                url = lot.get('href', '')
                offer_id = url.split('=')[-1] if '=' in url else url.rstrip('/').split('/')[-1]
                return [{
                        'filtration': 'все',
                        'price': lot_price,
                        'offer_id': offer_id,
                        'owner_username': owner_username
                    }]
            except Exception:
                raise fpx_err.FpxParseError('Не удалось распарсить категорию без фильтров.')
        for lot in lots:
            lot_f_values = [val.strip().lower() for key, val in lot.attrs.items() if key.startswith('data-f-')]
            for f in filters:
                if f in lot_f_values:
                    try:
                        price_div = lot.find('div', class_='tc-price') or lot.find('div', attrs={'data-s': True})
                        lot_price = float(price_div.get('data-s', 0)) if price_div else 0.0
                        if lot_price in (1.0, 0.0) or not price_div:
                            target_div = price_div or lot
                            raw_text = target_div.get_text(strip=True).replace(',', '.')
                            cleaned = "".join(c for c in raw_text if c.isdigit() or c == '.')
                            lot_price = float(cleaned) if cleaned else 0.0
                        if f not in lowcoasters or lot_price < lowcoasters[f]['price']:
                            username_el = lot.find('span', class_='pseudo-a') or lot.select_one('.media-user-name span')
                            owner_username = username_el.get_text(strip=True) if username_el else "Unknown"
                            url = lot.get('href', '')
                            offer_id = url.split('=')[-1] if '=' in url else url
                            lowcoasters[f] = {
                                'filtration': f,
                                'price': lot_price,
                                'offer_id': offer_id,
                                'owner_username': owner_username
                            }
                    except Exception:
                        logger.debug('При парсинге конкретного лота в категории что-то пошло не так')
                        continue
        return list(lowcoasters.values())