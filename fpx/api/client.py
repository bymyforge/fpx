import json
import urllib.parse


class FunPayClient:
    def __init__(self, account, http_client):
        self._account = account
        self.client = http_client

    async def get_chats_page(self) -> str:
        r = await self._account._request_engine.execute('GET', '/chat/')
        return r.text

    async def get_finance_page(self) -> str:
        r = await self._account._request_engine.execute('GET', '/account/balance')
        return r.text

    async def send_message_request(self, node_name, last_msg, text):
        request_data = {
        "action": "chat_message",
        "data": {
            "node": node_name,
            "last_message": last_msg,
            "content": text
        }
    }
        payload = {
            'request': json.dumps(request_data)
        }
        headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://funpay.com/chat/?node={node_name.split('-')[-1]}"
    }
        r = await self._account._request_engine.execute('POST', '/runner/', data=payload, headers=headers)
        return r.json()

    async def get_current_chat(self, chat_id):
        r = await self._account._request_engine.execute('GET', f'/chat/?node={chat_id}')
        return r.text

    async def get_user_profile(self, user_id):
        r = await self._account._request_engine.execute('GET', f'/users/{user_id}/')
        return r.text

    async def lot_menu_by_category(self, category_id):
        r = await self._account._request_engine.execute('GET', f'/lots/{category_id}/trade')
        return r.text

    async def get_main_menu(self):
        r = await self._account._request_engine.execute('GET', '/')
        return r.text

    async def raise_lot(self, node_id, game_id):
        payload = {
            'game_id': game_id,
            'node_id': node_id
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest"
        }
        r = await self._account._request_engine.execute('POST', '/lots/raise', data=payload, headers=headers)
        if "application/json" in r.headers.get("Content-Type", ""):
            response = r.json()
            return response.get('msg')
        else:
            return {"error": "not_json", "status": r.status_code}
            
    async def get_lot_info(self, lot_id):
        r = await self._account._request_engine.execute('GET', f'/lots/offer?id={lot_id}')
        return r.text

    async def get_my_sells(self):
        r = await self._account._request_engine.execute('GET', '/orders/trade')
        return r.text

    async def refund_order(self, csrf_token, order_id):
        url = f'/orders/refund'
        payload = {
            'id': order_id
        }
        r = await self._account._request_engine.execute('POST', url, data=payload)
        return r

    async def get_order_info(self, order_id):
        r = await self._account._request_engine.execute('GET', f'/orders/{order_id}/')
        return r.text

    async def get_lot_editor_data(self, lot_id):
        r = await self._account._request_engine.execute('GET', f'/lots/offerEdit?offer={lot_id}')
        return r.text

    async def edit_lot(self, lot, active=None):
        payload = {
            'form_created_at': lot.form_created_at,
            'offer_id': lot.offer_id,
            'node_id': lot.node_id,
            'location': lot.location if lot.location else 'offer',
            'deleted': lot.deleted,
        }
        payload.update(lot.fields)
        payload.pop('query', None)
        if active is not None:
            if active:
                payload['active'] = 'on'
            else:
                payload.pop('active', None)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://funpay.com/lots/offerEdit?node={lot.node_id}&offer={lot.offer_id}&location=offer',
        }
        r = await self._account._request_engine.execute('POST', '/lots/offerSave', data=payload, headers=headers)
        return r

    async def answer_review(self, authorid: str, text: str, orderid: str):
        payload = {
            'authorId': authorid,
            'text': text,
            'rating': '',
            'orderId': orderid
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest"
        }
        response = await self._account._request_engine.execute('POST', '/orders/review', data=payload, headers=headers)
        return response