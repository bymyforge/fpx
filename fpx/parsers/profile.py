import json
import logging

from bs4 import BeautifulSoup

from fpx.utils import errors as fpx_err
from .base import BaseParser

logger = logging.getLogger("fpx.profile_parser")


class ProfileParser(BaseParser):
    @classmethod
    def parse_finanses(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        balances_container = soup.find('span', class_='balances-list')
        if not balances_container:
            raise fpx_err.FpxNullDataError('На странице финансов не найдено модуля баланса')
        values = balances_container.find_all('span', class_='balances-value')
        if not values:
            raise fpx_err.FpxNullDataError('На странице финансов не найдено баланса')
        clean_values = [v.text.strip() for v in values]
        data = {}
        for i in clean_values:
            try:
                value = i.replace('₽', '').replace('$', '').replace('€', '').replace(',', '.').strip()
                num = float(value)
                if '₽' in i: data['rub'] = num
                elif '$' in i: data['usd'] = num
                elif '€' in i: data['eur'] = num
            except Exception as e:
                logger.debug(f'Ошибка парсинга отдельной валюты: {e}. Пропускаем')
                continue
        if not data:
            raise fpx_err.FpxParseError('Не удалось распарсить ни одну валюту, верстка полностью изменилась или что-то сломалось.')
        return Balance(**data)

    @classmethod
    def parse_profile(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        offer_list = soup.find_all('div', class_='offer')
        review_list = soup.find_all('div', class_='review-compiled-review')
        if not offer_list or not review_list:
            logger.debug('На странице профиля не найден блок категорий или блок отзывов. Возможно ошибка или их просто не существует')
        category_ids = set()
        lots = []
        for offer in offer_list:
            links = offer.find_all('a', href=True)
            if not links:
                logger.debug('В блоке категории не найдено лотов. Возможно ошибка/Их просто не существует')
            for link in links:
                try:
                    href = link['href']
                    if '/lots/' in href and 'id=' not in href:
                        cat_id = href.strip('/').split('/')[-1]
                        if cat_id.isdigit():
                            category_ids.add(cat_id)
                    if 'id=' in href:
                        lot_id = href.split('id=')[-1].split('&')[0]
                        name_tag = link.find('div', class_='tc-desc-text')
                        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                        lots.append({'name': name, 'id': lot_id})
                except Exception as e:
                    logger.debug(f'Ошибка парсинга отдельной категории: {e}')
                    continue
        if not lots:
            logger.debug('Не удалось распарсить ни один лот. Возможно изменилась вёрстка/у вас просто нет лотов.')
        reviews = []
        for review in review_list:
            try:
                rev = {}
                rev['text'] = review.find('div', class_='review-item-text').get_text(strip=True)
                rate_div = review.find('div', class_='rating').find('div', class_=True)
                rating = rate_div['class'][0]
                rev['stars'] = int(rating.replace('rating', ''))
                rev['author'] = review.find('div', class_='media-user-name').get_text(strip=True)
                rev['detail'] = review.find('div', class_='review-item-detail').get_text(strip=True)
                order_id = review.find('div', class_='review-item-order')
                rev['order_id'] = order_id.find('a').get('href').split('/')[-2]
                reviews.append(rev)
            except Exception as e:
                logger.debug(f'При парсинге конкретного отзыва возникла ошибка: {e}')
                continue
        if not reviews:
            logger.debug('Не удалось распарсить ни один отзыв, возможно их просто нет/возникла какая-то ошибка')
        return {'category-ids': list(category_ids), 'lots': lots, 'reviews': reviews}

    @classmethod
    def parse_my_sells(html_content):
        result = []
        soup = BeautifulSoup(html_content, 'html.parser')
        tc_items = soup.find_all('a', class_='tc-item')
        if not tc_items:
            raise fpx_err.FpxNullDataError('На странице продаж не найдено объектов(tc-item)')
        for item in tc_items:
            try:
                pre_result = {}
                order_tag = item.find('div', class_='tc-order')
                pre_result['order-id'] = order_tag.get_text(strip=True).replace('#', '') if order_tag else "Unknown"
                time_tag = item.find('div', class_='tc-date-time')
                pre_result['order-time'] = time_tag.get_text(strip=True) if time_tag else ""
                status_tag = item.find('div', class_='tc-status')
                pre_result['status'] = status_tag.get_text(strip=True) if status_tag else "Unknown"
                client_tag = item.find('span', class_='pseudo-a') or item.find('div', class_='tc-user')
                pre_result['client-name'] = client_tag.get_text(strip=True) if client_tag else "Unknown"
                price_tag = item.find('div', class_='tc-price')
                if price_tag:
                    raw_price = price_tag.get_text(strip=True).replace(',', '.')
                    cleaned_price = "".join(c for c in raw_price if c.isdigit() or c == '.')
                    pre_result['price'] = float(cleaned_price) if cleaned_price else 0.0
                else:
                    pre_result['price'] = 0.0
                order_desc = item.find('div', class_='order-desc')
                if order_desc:
                    divs = order_desc.find_all('div')
                    pre_result['name'] = divs[0].get_text(strip=True) if len(divs) > 0 else "Unknown"
                    pre_result['category'] = divs[1].get_text(strip=True) if len(divs) > 1 else "Unknown"
                else:
                    pre_result['name'] = "Unknown"
                    pre_result['category'] = "Unknown"
                result.append(pre_result)
            except Exception as e:
                logger.debug(f'При парсинге конкретного объекта произошла ошибка: {e}')
                continue
        if not result:
            raise fpx_err.FpxParseError('При парсинге не найдено ни одной продажи')
        return result

    @classmethod
    def parse_main_menu(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        user_link = soup.find('a', class_='user-link-dropdown')
        result = {}
        if user_link:
            href = user_link.get('href', '')
            user_id = href.strip('/').split('/')[-1]
            if user_id.isdigit():
                result['user-id'] = user_id
                result['username'] = soup.find('div', class_='user-link-name').get_text(strip=True)
            else:
                raise fpx_err.FpxParseError('Не удалось извлечь цифровой ID юзера, возможно слетела сессия или изменилась вёрстка')
        else:
            raise fpx_err.FpxNullDataError('На главной странице не найдено информации о юзере. Возможно слетела сессия')
        body = soup.find('body')
        if not body:
            raise fpx_err.FpxNullDataError('Тело главной страницы (body) не найдено')
        try:
            app_data_str = body.get('data-app-data', '{}')
            app_data = json.loads(app_data_str)
            result['csrf-token'] = app_data.get('csrf-token', '')
        except Exception:
            raise fpx_err.FpxParseError('Не удалось распарсить csrf_token из data-app-data.')
        return result