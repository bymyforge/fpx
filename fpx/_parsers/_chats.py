import json
import logging
import re
from typing import Any

from bs4 import BeautifulSoup

from fpx.models.chat import Chat
from fpx.utils import errors as fpx_err

from ._base import BaseParser

logger = logging.getLogger("fpx.chat_parser")


class ChatParser(BaseParser):

    @classmethod
    def parse_chats_list(cls, html_content: str) -> list[Chat]:
        '''Парсит страницу https://funpay.com/chat/'''
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('a', class_='contact-item')
        if not items:
            items = cls._safe_parse_links(html_content, r'node=\d+')
        if not items:
            raise fpx_err.FpxNullDataError('На странице не найдено ни одного чата')
        chats = []
        for item in items:
            try:
                href = str(item.get('href', ''))
                node_msg_id = int(str(item.get('data-node-msg', '0')))
                chat_id = href.split('node=')[-1] if 'node=' in href else ''
                username = cls.clean_text(item.find('div', class_='media-user-name'))
                last_msg = cls.clean_text(item.find('div', class_='contact-item-message'))
                date = cls.clean_text(item.find('div', class_='contact-item-time'))
                is_unread = 'unread' in (item.get('class', '') or [])
                chats.append(Chat(
                    id=chat_id, node_msg_id=node_msg_id, username=username, last_msg=last_msg,
                    date=date, link=href, is_unread=is_unread
                ))
            except Exception as e:
                logger.debug(f'Ошибка парсинга отдельного чата: {e}. Пропускаем элемент.')
                continue
        if not chats:
            raise fpx_err.FpxParseError(
                "Не удалось распарсить ни один чат, верстка полностью изменилась, или что-то сломалось."
            )
        return chats

    @classmethod
    def parse_chat(cls, html_content: str):
        ''' Парсит страницу https://funpay.com/chat/?node=...'''
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        chat_div = soup.find('div', class_='chat')
        if not chat_div:
            chat_div = soup.find('div', attrs={'data-id': re.compile(r'^\d+$')})
        body = soup.find('body')
        if not chat_div or not body:
            raise fpx_err.FpxNullDataError('На странице чата не найден блок переписки или тег body')
        chats = soup.find_all('div', class_='chat-msg-item')
        if chats:
            try:
                chat = chats[-1]
                res: dict[str, Any] = {'is_system': False}
                msg_tag = chat.find('div', class_='chat-msg-text')
                if msg_tag:
                    message = msg_tag.get_text(separator='\n').strip() if msg_tag else ''
                    if not message:
                        img_link = msg_tag.find('a', class_='chat-img-link')
                        message = img_link.get('href', '') if img_link else '' # type: ignore[assignment]
                    res['message'] = message
                else:
                    res['message'] = ''
                author_block = None
                current_node = chat
                while current_node:
                    author_block = current_node.find('div', class_='media-user-name')
                    if author_block:
                        break
                    current_node = current_node.find_previous_sibling('div', class_='chat-msg-item') # type: ignore[assignment]
                if author_block:
                    author = author_block.find('a', class_='chat-msg-author-link')
                    if not author:
                        sender_lbl = author_block.find('span', class_='chat-msg-author-label')
                        res['sender'] = cls.clean_text(sender_lbl) if sender_lbl else "FunPay"
                        if res['sender'] and res['sender'].lower() == 'оповещение':
                            res['sender'] = 'FunPay' # type: ignore[assignment]
                            res['is_system'] = True
                    else:
                        res['sender'] = author.get_text(strip=True) # type: ignore[assignment]
                else:
                    res['sender'] = "Unknown" # type: ignore[assignment]
                result['last_message'] = res
            except Exception as e:
                logger.debug(f"Не удалось распарсить последнее сообщение в чате: {e}")
                result['last_message'] = None # type: ignore[assignment]
        else:
            logger.debug('Последнее сообщение не найдено!')
            result['last_message'] = None # type: ignore[assignment]
            # парсинг тех.данных
        try:
            result['data-name'] = chat_div.get('data-name', '') # type: ignore[assignment]
            app_data_str = str(body.get('data-app-data', '{}') or '{}')
            app_data = json.loads(app_data_str)
            result['csrf-token'] = app_data.get('csrf-token', '')
            result['user-id'] = app_data.get('userId', '')
        except Exception as e:
            logger.debug(f"Ошибка извлечения системных данных чата: {e}")
            raise fpx_err.FpxParseError("Не удалось распарсить системные метаданные чата (CSRF/User ID)")
        return result
