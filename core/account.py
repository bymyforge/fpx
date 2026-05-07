import httpx
from bs4 import BeautifulSoup
from models.chat import ChatData
from api.client import FunPayClient
from api.parsers import FunPayParser


class Account:
    def __init__(self, client):
        self.http_client = client
        self.client = FunPayClient(self.http_client)
        self.parser = FunPayParser()
        self.user_id = None
        self.csrf_token = None
        self.last_msg_ids = {}
        self.node_names = {}

    async def get_chats(self):
        '''

        The function calls the chats in account, returns an object with values:  
        id: str, Chat id (node)  
        username: str, Client nickname  
        last_msg: str, Last message in chat  
        date: str, last message date  
        link: str, full chat link (https://funpay.com/chat/?node=id)  
        is_unread: bool, Readed or not  
          
        '''
        html = await self.client.get_chats_page()
        chats = self.parser.parse_chats_list(html)
        for chat in chats:
            if chat.id not in self.last_msg_ids:
                self.last_msg_ids[chat.id] = chat.node_msg_id
        return chats

    async def get_balance(self):
        '''

        The function calls the account balance, returns an object with values:  
        rub: float  
        usd: float  
        eur: float  
          
        '''
        html = await self.client.get_finance_page()
        balance = self.parser.parse_finanses(html)
        return balance

    async def send_message(self, chat_id:str, text:str):
        if chat_id not in self.node_names or not self.csrf_token:
            await self.get_chat_data(chat_id)
        last_id = self.last_msg_ids.get(chat_id, 0)
        response = await self.client.send_message_request(self.node_names[chat_id], last_id, text, self.csrf_token)
        if response.get('id'):
            self.last_msg_ids[chat_id] = response.get('id')
        return response

    async def get_chat_data(self, chat_id):
        html = await self.client.get_current_chat(chat_id)
        data = self.parser.parse_chat(html)
        chat = ChatData(node_name=data['data-name'], csrf_token=data['csrf-token'], user_id=data['user-id'])
        self.node_names[chat_id] = chat.node_name
        self.csrf_token = chat.csrf_token
        self.user_id = chat.user_id
        return chat