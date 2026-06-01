
import json
import logging

from bs4 import BeautifulSoup

from fpx.models.chat import Chat
from fpx.models.account import Balance
from fpx.utils import errors as fpx_err

logger = logging.getLogger("fpx.parser")

class FunPayParser:
    @staticmethod
    def parse_chats_list(html_content: str) -> list[Chat]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('a', class_='contact-item')
        if not items:
            raise fpx_err.FpxNullDataError('На странице не найдено ни одного чата')
        chats = []
        for item in items:
            try:
                href = item.get('href', '')
                node_msg_id = item.get('data-node-msg', '0')
                chat_id = href.split('node=')[-1] if 'node=' in href else ''
                username = item.find('div', class_='media-user-name').text.strip()
                last_msg = item.find('div', class_='contact-item-message').text.strip()
                date = item.find('div', class_='contact-item-time').text.strip()
                is_unread = 'unread' in item.get('class', [])
                chats.append(Chat(
                    id=chat_id, node_msg_id=int(node_msg_id), username=username, last_msg=last_msg,
                    date=date, link=href, is_unread=is_unread
                ))
            except Exception as e:
                logger.debug(f'Ошибка парсинга отдельного чата: {e}. Пропускаем элемент.')
                continue
        if not chats:
            raise fpx_err.FpxParseError("Не удалось распарсить ни один чат, верстка полностью изменилась, или что-то сломалось.")
        return chats

    @staticmethod
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

    @staticmethod
    def parse_chat(html_content: str):
            soup = BeautifulSoup(html_content, 'html.parser')
            result = {}
            chat_div = soup.find('div', class_='chat')
            body = soup.find('body')
            if not chat_div or not body:
                raise fpx_err.FpxNullDataError('На странице чата не найден блок переписки или тег body')
            
            # парсинг чатов
            chats = soup.find_all('div', class_='chat-msg-item chat-msg-with-head')
            if chats:
                try:
                    chat = chats[-1]
                    res = {}
                    res['is_system'] = False
                    res['message'] = chat.find('div', class_='chat-msg-text').get_text(separator='\n').strip()
                    author = chat.find('a', class_='chat-msg-author-link')
                    if not author:
                        res['sender'] = chat.find('span', class_='chat-msg-author-label')
                        if res['sender']:
                            res['sender'] = res['sender'].get_text(strip=True)
                            if res['sender'] == 'оповещение':
                                res['sender'] = 'FunPay'
                                res['is_system'] = True
                    else:
                        res['sender'] = author.get_text(strip=True)
                    result['last_message'] = res
                except Exception as e:
                    logger.debug(f"Не удалось распарсить последнее сообщение в чате: {e}")
            else:
                result['last_message'] = None

            # парсинг тех.данных
            try:
                result['data-name'] = chat_div.get('data-name', '')
                app_data_str = body.get('data-app-data', '{}')
                app_data = json.loads(app_data_str)
                result['csrf-token'] = app_data.get('csrf-token', '')
                result['user-id'] = app_data.get('userId', '')
            except Exception as e:
                logger.debug(f"Ошибка извлечения системных данных чата: {e}")
                raise fpx_err.FpxParseError("Не удалось распарсить системные метаданные чата (CSRF/User ID)")
            return result

    @staticmethod
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
                reviews.append(rev)
            except Exception as e:
                logger.debug(f'При парсинге конкретного отзыва возникла ошибка: {e}')
                continue
        if not reviews:
            logger.debug('Не удалось распарсить ни один отзыв, возможно их просто нет/возникла какая-то ошибка')
        return {'category-ids': list(category_ids), 'lots': lots, 'reviews': reviews}
        
    @staticmethod
    def parse_lot_menu(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        button = soup.find('button', class_='js-lot-raise')
        if button:
            data_game = button.get('data-game')
            if data_game:
                return data_game
            raise fpx_err.FpxParseError('Атрибут data-game не найден внутри кнопки поднятия')
        raise fpx_err.FpxNullDataError('На странице лотов не найдена кнопка для поднятия (возможно, у вас нет лотов)')

    @staticmethod
    def parse_main_menu(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        user_link = soup.find('a', class_='user-link-dropdown')
        result = {}
        if user_link:
            href = user_link.get('href', '')
            user_id = href.strip('/').split('/')[-1]
            if user_id.isdigit():
                result['user-id'] = user_id
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
        
    @staticmethod
    def parse_current_lot_menu(html_content):
        result = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        param_items = soup.find_all('div', class_='param-item')
        if not param_items:
            raise fpx_err.FpxNullDataError('Страница лота не найдена. Возможно, указана инвалидная ссылка или лот был удалён.')
        else:
            descriptions = {}
            for item in param_items:
                try:
                    header = item.find('h5').get_text(strip=True)
                    text = item.find('div').get_text(separator='\n', strip=True)
                    descriptions[header] = text
                except Exception as e:
                    logger.debug(f'При парсинге конкретного объекта произошла ошибка: {e}')
            result['short_desc'] = descriptions.get('Краткое описание')
            result['description'] = descriptions.get('Подробное описание')
            option = soup.find('option', value='21') or soup.find('option', attrs={'data-content': True})
            if option:
                inner_html = option.get('data-content')
                if inner_html:
                    inner_soup = BeautifulSoup(inner_html, 'html.parser')
                    price_span = inner_soup.find('span', class_='payment-value')
                    if price_span:
                        raw_price = price_span.get_text(strip=True).replace(',', '.')
                        cleaned_price = "".join(c for c in raw_price if c.isdigit() or c == '.')
                        try:
                            result['price'] = float(cleaned_price) if cleaned_price else 0.0
                        except ValueError:
                            result['price'] = 0.0
                        return result
            raise fpx_err.FpxNullDataError('Не удалось найти цену в скрытых атрибутах выбора оплаты.')

    @staticmethod
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

    @staticmethod
    def parse_order_page(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        result['review'] = {}
        try:
            header = soup.find('h1', class_='page-header')
            if not header:
                raise fpx_err.FpxNullDataError('Страница заказа не найдена, возможно, указан неверный ID или слетела сессия.')
            spans = header.find_all('span')
            if not spans:
                raise fpx_err.FpxParseError('Не удалось распарсить статус заказа из заголовка.')
            result['status'] = " / ".join([span.get_text(strip=True) for span in spans])
            review_container = soup.find('div', class_='review-container')
            if review_container:
                try:
                    text_tag = review_container.find('div', class_='review-item-text')
                    result['review']['text'] = text_tag.get_text(strip=True) if text_tag else ''
                    raw_stars = review_container.get('data-rating', '0')
                    result['review']['stars'] = int(raw_stars) if raw_stars.isdigit() else 0
                    answer_div = review_container.find('div', class_='review-item-answer')
                    if answer_div:
                        text_container = answer_div.find('div')
                        result['review']['answer'] = text_container.get_text('\n', strip=True) if text_container else ''
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

    @staticmethod
    def parse_edit_lot_page(html_content):
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
                        result[name] = t.string if t.string else ''
                except Exception as e:
                    logger.debug(f'При парсинге конкретного текстового поля произошла ошибка: {e}')
        return result