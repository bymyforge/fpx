# Чаты и сообщения

Всё что связано с получением, отправкой и обработкой сообщений.

---

## Хендлеры (через роутер)

Основной способ — через `@fp.router.on_message()`. Подробно описано в разделе [Роутер](router.md).

```python
@fp.router.on_message()
async def any_msg(message: Message):
    print(f'{message.sender}: {message.text}')
    await message.answer('Принято')
```

### Команды

```python
async def status_cmd(message: Message):
    await message.answer('Бот работает')

fp.router.message_commands({'!status': status_cmd})
```

---

## Объект Message

Прилетает в хендлеры. Содержит:

| Поле | Тип | Описание |
|------|-----|----------|
| `sender` | `str` | Ник отправителя |
| `chat_id` | `str` | ID чата (node) |
| `text` | `str` | Текст сообщения |
| `is_system` | `bool` | Системное ли сообщение |

### Методы

**`await message.answer(answer_text: str)`** — ответить в тот же чат. Поддерживает форматирование:
- `{sender}` — ник отправителя
- `{chat_id}` — ID чата
- `{text}` — текст сообщения

```python
await message.answer('Привет, {sender}! Твой ID чата: {chat_id}')
```

---

## ChatManager (через account.chat)

Методы для работы с чатами напрямую, вне хендлеров.

### `await fp.account.chat.get_chats()`

Возвращает список всех чатов на аккаунте.

```python
chats = await fp.account.chat.get_chats()
for chat in chats:
    print(f'{chat.username}: {chat.last_msg}')
```

Возвращает `list[Chat]`, каждый объект содержит:
- `id` — ID чата (node)
- `username` — Ник собеседника
- `last_msg` — Последнее сообщение
- `date` — Дата
- `link` — Ссылка на чат
- `is_unread` — Непрочитанное ли

### `await fp.account.chat.send_message(chat_id, text)`

Отправить сообщение в чат по его ID.

```python
await fp.account.chat.send_message('12345678', 'Привет')
```

### `await fp.account.chat.get_chat_data(chat_id)`

Получает технические данные чата (csrf_token, node_name, последнее сообщение).

```python
data = await fp.account.chat.get_chat_data('12345678')
print(data.csrf_token)
print(data.last_message.text)
```

Возвращает `ChatData`:
- `node_name` — системный ID (например `users-12345-67890`)
- `csrf_token` — токен для POST-запросов
- `user_id` — твой ID
- `last_message` — объект `Message` (последнее сообщение)
