from models.chat import ChatData
from utils.errors import MessageNotDelivered

class ChatManager:
    def __init__(self, account):
        self.account = account

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
        html = await self.account.client.get_chats_page()
        chats = self.account.parser.parse_chats_list(html)
        for chat in chats:
            if chat.id not in self.account.last_msg_ids:
                self.account.last_msg_ids[chat.id] = chat.node_msg_id
        return chats

    async def send_message(self, chat_id:str, text:str):
        '''
        The function takes chat_id, text.  
        Sends a message to the given chat, on success it returns 'succes', on error it returns the error MessageNotDelivered
        '''
        if chat_id not in self.account.node_names or not self.account.csrf_token:
            await self.get_chat_data(chat_id)
        response = await self.account.client.send_message_request(self.account.node_names[chat_id], -1, text, self.account.csrf_token)
        inner_response = response.get('response', {})
        if inner_response.get('error') is None:
            return 'success'
        else:
            error_msg = inner_response.get('error', 'Unknown error')
            raise MessageNotDelivered(f'Server returned a error: {error_msg}')

    async def get_chat_data(self, chat_id):
        '''
        https://funpay.com/chat/?node={chat_id}
        '''
        html = await self.account.client.get_current_chat(chat_id)
        data = self.account.parser.parse_chat(html)
        chat = ChatData(node_name=data['data-name'], csrf_token=data['csrf-token'], user_id=data['user-id'])
        self.account.node_names[chat_id] = chat.node_name
        self.account.csrf_token = chat.csrf_token
        self.account.user_id = chat.user_id
        return chat