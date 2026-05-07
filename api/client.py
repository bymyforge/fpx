import json



class FunPayClient:
    def __init__(self, http_client):
        self.client = http_client

    async def get_chats_page(self) -> str:
        r = await self.client.get('/chat/')
        return r.text

    async def get_finance_page(self) -> str:
        r = await self.client.get('/account/balance')
        return r.text

    async def send_message_request(self, node_name, last_msg, text, csrf_token):
        request_data = {
        "action": "chat_message",
        "data": {
            "node": node_name,
            "last_message": last_msg,
            "content": text
        }
    }
        payload = {
            'request': json.dumps(request_data),
            'csrf_token': csrf_token
        }
        headers = {
        "X-Requested-With": "XMLHttpRequest",
        "X-Cp-Csrf-Token": csrf_token,
        "Referer": f"https://funpay.com/chat/?node={node_name.split('-')[-1]}"
    }
        r = await self.client.post('/chat/message/', data=payload, headers=headers)
        print(f"DEBUG | Статус: {r.status_code}")
        print(f"DEBUG | Ответ: {r.text}")
        return r.json()

    async def get_current_chat(self, chat_id):
        r = await self.client.get(f'/chat/?node={chat_id}')
        return r.text