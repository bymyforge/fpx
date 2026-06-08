import inspect
import logging
import asyncio

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
                    stop_words = ('оплатил заказ', 'можете перейти в discord', 'написал отзыв', 'изменил отзыв', 'вернул деньги', 'подтвердил успешное выполнение')
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
        for cmd_handler in self.runner.handler._handlers['commands']:
            target_command = cmd_handler['command']
            target_command_lower = {k.lower(): v for k, v in target_command.items()}
            if first_word in target_command_lower:
                target_function = target_command_lower[first_word]
                sig = inspect.signature(target_function)
                total_params_count = len(sig.parameters)
                has_state = False
                for param in sig.parameters.values():
                    if param.annotation == FSMContext:
                        has_state = True
                        break
                if has_state:
                    required_args = total_params_count - 2
                    alowed_args_count = max(0, required_args)
                    final_args = args[:alowed_args_count]
                    if len(args) < required_args:
                        param_names = list(sig.parameters.keys())
                        missing_param = param_names[2 + len(args)]
                        raise fpx_err.FpxCommandArgsError(target_function.__name__, missing_param)
                    await target_function(message, state_ctx, *final_args)
                else:
                    required_args = total_params_count - 1
                    alowed_args_count = max(0, required_args)
                    final_args = args[:alowed_args_count]
                    if len(args) < required_args:
                        param_names = list(sig.parameters.keys())
                        missing_param = param_names[1 + len(args)]
                        raise fpx_err.FpxCommandArgsError(target_function.__name__, missing_param)
                    await target_function(message, *final_args)
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
            if self.runner.handler._handlers['error']:
                await self.runner.handler._handlers['error'](message, e)
            else:
                logger.debug(f'Ошибка при обработке сообщения: {e}', exc_info=True)
            return
        for handler in self.runner.handler._handlers['message']:
            if handler['state'] != current_state:
                continue
            async def call_handler(h_func):
                sig = inspect.signature(h_func)
                has_state = False
                for param in sig.parameters.values():
                    if param.annotation == FSMContext:
                        has_state = True
                        break
                if has_state:
                    await h_func(message, state_ctx)
                else:
                    await h_func(message)
            if handler['state'] is not None:
                await call_handler(handler['function'])
                break
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
                if matched:
                    await call_handler(handler['function'])
                    break
            filter_text = handler['filter_text']
            if filter_text is None and handler['mapping'] is None:
                await call_handler(handler['function'])
                break
            if isinstance(filter_text, str) and msg_text.startswith(filter_text.lower()):
                await call_handler(handler['function'])
                break

    async def _check_chats(self):
        await self.runner._chat._update_chat_cache()
        chats = await self.runner._chat._compare_chat_cache()
        if chats:
            async def process_single_chat(chat_cache_obj):
                try:
                    msg_obj = await self.runner._account.chat.get_chat_data(chat_cache_obj.chat_id)
                    message = msg_obj.last_message
                    chat_msg = Message(
                        sender=message.sender, 
                        chat_id=chat_cache_obj.chat_id, 
                        text=chat_cache_obj.text, 
                        is_system=message.is_system
                    )   
                    chat_msg._client = self.runner
                    await self._trigger_message_handlers(chat_msg)
                except Exception as e:
                    logger.debug(f"Ошибка при параллельной обработке чата {chat_cache_obj.chat_id}: {e}", exc_info=True)
            tasks = [process_single_chat(chat) for chat in chats]
            await asyncio.gather(*tasks)