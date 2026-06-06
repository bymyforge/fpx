import json
import logging
import re

from bs4 import BeautifulSoup

from fpx.models.chat import Chat
from fpx.utils import errors as fpx_err
from .base import BaseParser

logger = logging.getLogger("fpx.chat_parser")


class ChatParser(BaseParser):

    @classmethod
    def parse_chats_list(cls, html_content: str) -> list[Chat]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('a', class_='contact-item')
        if not items:
            items = cls._safe_parse_links(html_content, r'node=\d+')
        if not items:
            raise fpx_err.FpxNullDataError('На странице не найдено ни одного чата')
        chats = []
        for item in items:
            try:
                href = item.get('href', '')
                node_msg_id = item.get('data-node-msg', '0')
                chat_id = href.split('node=')[-1] if 'node=' in href else ''
                username = cls.clean_text(item.find('div', class_='media-user-name'))
                last_msg = cls.clean_text(item.find('div', class_='contact-item-message'))
                date = cls.clean_text(item.find('div', class_='contact-item-time'))
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

    @classmethod
    def parse_chat(cls, html_content: str):
            soup = BeautifulSoup(html_content, 'html.parser')
            result = {}
            chat_div = soup.find('div', class_='chat')
            if not chat_div:
                chat_div = soup.find('div', attrs={'data-id': re.compile(r'^\d+$')})
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
                    msg_tag = chat.find('div', class_='chat-msg-text')
                    res['message'] = msg.get_text(separator='\n').strip() if msg_tag else ''
                    author = chat.find('a', class_='chat-msg-author-link')
                    if not author:
                        sender_lbl = chat.find('span', class_='chat-msg-author-label')
                        res['sender'] = cls.clean_text(sender_lbl)
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
                    result['last_message'] = None
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