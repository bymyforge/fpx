# Машина состояний (FSM)

Для пошаговых диалогов. Каждый чат имеет свой независимый контекст.

---

## Как работает

- **Storage** - хранилище состояний. По умолчанию `MemoryStorage` (в оператвной памяти, сбрасывается при перезапуске). Есть `FileStorage` (сохраняет в JSON файл) и `RedisStorage` (Redis, не теряет данные при перезапуске).
- **FSMContext** - объект, через который управляешь состоянием конкретного чата.

---

## Пример диалога

```python
from fpx import FunPayTools, Message
from fpx.fsm import FSMContext

fp = FunPayTools('gkey')

@fp.router.on_message(text='!start')
async def start_dialog(message: Message, state: FSMContext):
    await message.answer('Привет, введи свой ник')
    await state.set_state('waiting_nickname')

@fp.router.on_message(state='waiting_nickname')
async def get_nickname(message: Message, state: FSMContext):
    nick = message.text
    await state.update_data(nick=nick)
    await message.answer('Теперь введи пароль')
    await state.set_state('waiting_pass')

@fp.router.on_message(state='waiting_pass')
async def get_pass(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer('Вы уверены? Да/Нет')
    await state.set_state('waiting_confirm')

@fp.router.on_message(state='waiting_confirm')
async def get_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"Принято! Ник: {data.get('nick')}, пароль: {data.get('password')}")
    await state.clear_state()
```

---

## FSMContext методы

| Метод | Принимает | Возвращает | Описание |
|-------|-----------|------------|----------|
| `await state.set_state(state)` | `str` или `None` | - | Установить стейт. `None` - сбросить |
| `await state.get_state()` | - | `str` или `None` | Текущий стейт |
| `await state.update_data(**kwargs)` | kwargs | - | Сохранить данные |
| `await state.get_data()` | - | `dict` | Получить сохранённые данные |
| `await state.clear_state()` | - | - | Удалить стейт и данные |

---

## Хранилища

### MemoryStorage (по умолчанию)

```python
from fpx import FunPayTools

fp = FunPayTools('gkey')  # MemoryStorage используется автоматически
```

Данные хранятся в памяти процесса. **Сбрасываются при перезапуске.**

---

### FileStorage

```python
from fpx import FunPayTools
from fpx.fsm import FileStorage

fp = FunPayTools('gkey', storage=FileStorage('states.json'))
```

Состояния сохраняются в JSON файл который вы укажете в аргументах и **переживают перезапуск**.

---

### RedisStorage

Хранит состояния в Redis. Данные **переживают перезапуск** и доступны между несколькими процессами.

**Установка зависимости:**

```bash
pip install fpx-engine[redis]
```

**Использование:**

```python
from fpx import FunPayTools
from fpx.fsm import RedisStorage

storage = RedisStorage(
    url='redis://localhost:6379',  # по умолчанию
    prefix='fpx'                  # префикс ключей в Redis, по умолчанию 'fpx'
)

fp = FunPayTools('gkey', storage=storage)
```

Ключи хранятся в формате `{prefix}:fsm:{chat_id}`, например `fpx:fsm:12345`.

> ⚠️ **Предупреждение:** При конкурентном доступе к одному `chat_id` возможна потеря данных (race condition). Для высоких нагрузок рекомендуется использовать Redis Lua-скрипты.

---

### Кастомное хранилище

Наследуйся от `BaseStorage` и переопредели методы:

```python
from fpx.fsm import BaseStorage

class MyStorage(BaseStorage):
    async def set_state(self, chat_id: str | int, state: str | None) -> None:
        # твоя логика
        pass

    async def get_state(self, chat_id: str | int) -> str | None:
        pass

    async def update_data(self, chat_id: str | int, **kwargs) -> None:
        pass

    async def get_data(self, chat_id: str | int) -> dict:
        return {}

    async def clear_state(self, chat_id: str | int) -> None:
        pass
```

---

## Сравнение хранилищ

| Хранилище | Переживает перезапуск | Несколько процессов | Зависимости |
|-----------|:---------------------:|:-------------------:|-------------|
| `MemoryStorage` | ❌ | ❌ | нет |
| `FileStorage` | ✅ | ❌ | нет |
| `RedisStorage` | ✅ | ✅ | `pip install fpx-engine[redis]` |

---

## Dependency

Можно прокидывать зависимости в хендлеры через `Dependency`. Пример из роутера команд:

```python
from fpx import Dependency

async def get_cur_user(message: Message):
    return {'id': message.sender, 'vip': True}

@fp.router.on_message(state='waiting_nickname')
async def handler(message: Message, user: User = Dependency(get_cur_user)):
    print(user)
```

Функция зависимость получает `message` и `state` автоматически и возвращает объект, который попадает в параметр хендлера.
