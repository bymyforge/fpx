import logging
import json
from bs4 import BeautifulSoup

from models.chat import Chat
from models.account import Balance
from utils.errors import NullData

class FunPayParser:

    @staticmethod
    def parse_chats_list(html_content: str) -> list[Chat]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.find_all('a', class_='contact-item')
        chats = []
        for item in items:
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
        return chats

    @staticmethod
    def parse_finanses(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        balances_container = soup.find('span', class_='balances-list')
        if not balances_container:
            raise NullData()
        values = balances_container.find_all('span', class_='balances-value')
        clean_values = [v.text.strip() for v in values]
        data = {}
        for i in clean_values:
            value = i.replace('₽', '').replace('$', '').replace('€', '').replace(',', '.').strip()
            num = float(value)
            if '₽' in i: data['rub'] = num
            elif '$' in i: data['usd'] = num
            elif '€' in i: data['eur'] = num
        return Balance(**data)

    @staticmethod
    def parse_chat(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            result = {}
            chat_div = soup.find('div', class_='chat')
            if chat_div:
                result['data-name'] = chat_div.get('data-name', '')
            else:
                raise NullData('Chat block is not found')
            body = soup.find('body')
            if not body:
                raise NullData('Body tag is not found')
            app_data_str = body.get('data-app-data', '{}')
            app_data = json.loads(app_data_str)
            result['csrf-token'] = app_data.get('csrf-token', '')
            result['user-id'] = app_data.get('userId', '')
            return result
        except Exception as e:
            logging.error(e)