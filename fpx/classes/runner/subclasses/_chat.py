import inspect
import logging
import asyncio
import re

from fpx.models.chat import Message
from fpx.fsm import FSMContext
from fpx.utils import errors as fpx_err

logger = logging.getLogger("fpx.chat_runner")

class ChatRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _compare_chat_cache(self):
        '''
        Сравнивает старый кеш сообщений с новым, если находит отличия, выносит сообщение в список, после чего возвращает полный список
        '''
        result = []
        if self.runner._cache['msgs'] != self.runner._cache['old_msgs']:
            for message in self.runner._cache['msgs']:
                if message not in self.runner._cache['old_msgs']:
                    stop_words = ('оплатил заказ', 'можете перейти в discord', 'написал отзыв', 'изменил отзыв', 'вернул деньги', 'подтвердил успешное выполнение', 'удалил отзыв', 'оплатив замовлення', 'можете перейти в discord', 'написав відгук', 'змінив відгук', 'повернув гроші', 'підтвердив успішне виконання', 'видалив відгук', 'paid for the order', 'you can go to discord', 'left a review', 'changed the review', 'refunded money', 'confirmed successful completion', 'deleted the review')
                    msg_lower = message['last_msg'].lower()
                    if not any(word in msg_lower for word in stop_words):
                        result.append(Message(sender=message['sender'], chat_id=message['chat_id'], text=message['last_msg'], is_system=False))
        return result

    async def _update_chat_cache(self):
        '''
        Обновляет кеш последних чатов
        '''
        chats = await self.runner._account.chat.get_chats()
        result = []
        counter = 0
        for chat in chats:
            if counter > 75:
                break
            chat = {'sender': chat.username, 'chat_id': chat.id, 'last_msg': chat.last_msg}
            result.append(chat)
            counter += 1
        self.runner._cache['old_msgs'] = self.runner._cache['msgs']
        self.runner._cache['msgs'] = result

    async def _process_message(self, message: Message, state_ctx):
        if not message.text:
            return False
        parts = message.text.split()
        if not parts:
            return False
        first_word = parts[0].lower()
        args = parts[1:]
        for cmd_handler in self.runner.router._handlers['commands']:
            target_command = cmd_handler['command']
            target_command_lower = {k.lower(): v for k, v in target_command.items()}
            if first_word in target_command_lower:
                target_function = target_command_lower[first_word]
                sig = inspect.signature(target_function)
                text_param_names = [
                    name for name, param in sig.parameters.items()
                    if param.annotation == str and param.default is inspect.Parameter.empty
                    and param.annotation not in (Message, FSMContext)
                ]
                if len(args) < len(text_param_names):
                    missing_param = text_param_names[len(args)]
                    raise fpx_err.FpxCommandArgsError(target_function.__name__, missing_param)
                await self.runner.router.invoke(target_function, message, state_ctx)
                return True
        return False

    async def _check_text_filter(self, msg_text, filter_text, mapping):
        if filter_text is None:
            return True
        if isinstance(filter_text, str) and msg_text.startswith(filter_text.lower()):
            return True
        return False

    async def _check_contains_filter(self, msg_text, h_filter):
        if isinstance(h_filter, str):
            h_filter = [h_filter]
        if h_filter is not None:
            for element in h_filter:
                if element.lower() in msg_text:
                    return True
            return False
        return True

    async def _check_regex(self, msg_text, h_regex):
        if isinstance(h_regex, str):
            h_regex = [h_regex]
        if h_regex is not None:
            for element in h_regex:
                if re.search(element, msg_text):
                    return True
            return False
        return True

    async def _chat_id_check(self, msg: Message, h_chat_id):
        if isinstance(h_chat_id, str | int):
            h_chat_id = [h_chat_id]
        if h_chat_id is not None:
            for element in h_chat_id:
                if element == msg.chat_id:
                    return False
            return True
        return True

    async def _sender_check(self, msg: Message, h_sender):
        if isinstance(h_sender, str | int):
            h_sender = [h_sender]
        if h_sender is not None:
            for element in h_sender:
                if element == msg.sender:
                    return False
            return True
        return True

    async def _custom_check(self, msg, h_custom):
        if h_custom is not None:
            if asyncio.iscoroutinefunction(h_custom):
                is_match = await h_custom(msg)
            else:
                is_match = h_custom(msg)
            if is_match:
                return True
            return False
        return True

    async def _check_filters(self, message: Message, handler):
        msg_text = message.text.lower()
        if await self._check_text_filter(msg_text, handler['filter_text'], handler['mapping']):
            if await self._check_contains_filter(msg_text, handler['contains']):
                if await self._check_regex(msg_text, handler['regex']):
                    if await self._chat_id_check(message, handler['ignore_chat_id']):
                        if await self._sender_check(message, handler['ignore_sender']):
                            if await self._custom_check(message, handler['custom']):
                                return True
        return False

    async def _trigger_message_handlers(self, message):
        if self.runner._account.data.username is None:
            await self.runner._account.profile.get_user_data()
        if self.runner._account.data.username == message.sender:
            return
        msg_text = message.text.lower()
        current_state = await self.runner.storage.get_state(message.chat_id)
        state_ctx = FSMContext(storage=self.runner.storage, chat_id=message.chat_id)
        try:
            if await self._process_message(message, state_ctx):
                return
        except Exception as e:
            logger.debug(f'Ошибка при обработке сообщения: {e}', exc_info=True)
            await self.runner._handle_error(event=message, exception=e)
            return
        for handler in self.runner.router._handlers['message']:
            if handler['state'] != current_state:
                continue
            if not await self._check_filters(message, handler):
                continue
            if handler['mapping'] is not None:
                matched = False
                for trigger, reply in handler['mapping'].items():
                    if msg_text.startswith(trigger.lower()):
                        formatted_reply = reply.format(
                            sender=message.sender,
                            chat_id=message.chat_id,
                            text=message.text
                        )
                        await message.answer(formatted_reply)
                        matched = True
                        break
            await self.runner.router.invoke(handler['function'], message, state_ctx)
            break
            
    async def _check_chats(self):
        await self.runner._chat._update_chat_cache()
        chats = await self.runner._chat._compare_chat_cache()
        if chats:
            async def process_single_chat(chat_cache_obj):
                chat_msg = None
                try:
                    msg_obj = await self.runner._account.chat.get_chat_data(chat_cache_obj.chat_id)
                    message = msg_obj.last_message
                    if message is None:
                        return
                    stop_list = ['изображение', 'image', 'зображення']
                    text = chat_cache_obj.text if chat_cache_obj.text.lower() not in stop_list else message.text
                    chat_msg = Message(
                        sender=message.sender, 
                        chat_id=chat_cache_obj.chat_id, 
                        text=text, 
                        is_system=message.is_system
                    )   
                    chat_msg._client = self.runner
                    await self._trigger_message_handlers(chat_msg)
                except Exception as e:
                    logger.debug(f"Ошибка при параллельной обработке чата {chat_cache_obj.chat_id}: {e}", exc_info=True)
                    await self.runner._handle_error(event=chat_msg, exception=e)
            tasks = [process_single_chat(chat) for chat in chats]
            await asyncio.gather(*tasks)