<h1 align="center">🧠 Машина состояний (FSM)</h1>

<p>При создании сложных ботов часто нужно вести диалог с покупателем по шагам. Например: сначала бот ждет от пользователя ссылку, затем игровой ник, а только потом выдает товар. Для реализации такой логики в <code>fpx-engine</code> встроен инструмент <b>FSM (Finite State Machine)</b>.</p>

<p>Машина состояний автоматически привязывается к уникальному <code>chat_id</code> переписки, поэтому у каждого покупателя будет свой независимый контекст общения.</p>

<hr>

<h2>📦 1. Как это устроено под капотом</h2>

<ul>
  <li><b>Хранилище (Storage):</b> Базовый класс <code>BaseStorage</code> задает стандарт для сохранения стейтов. По умолчанию фреймворк предоставляет <code>MemoryStorage</code> — это быстрое хранилище в оперативной памяти (сбрасывается при перезапуске бота).</li>
  <li><b>Контекст (FSMContext):</b> Удобная прослойка, которая летает внутри ваших хендлеров. Через нее вы меняете состояния и сохраняете временные данные конкретного чата.</li>
</ul>

<hr>

<h2>💻 2. Пример реализации (Пошаговый диалог)</h2>

<p>Смотри, как легко реализовать скрипт, который активируется при новом сообщении, включает стейт ожидания никнейма, запоминает его и финализирует сделку:</p>

<pre><code class="language-python">from fpx import FunPayTools, Message
from fpx.fsm import FSMContext

fp = FunPayTools("ВАШ_GOLDEN_KEY")

# 1. Определяем строковые стейты для этапов диалога
class States:
    wait_for_nickname = "wait_for_nickname"
    wait_for_confirm = "wait_for_confirm"

# Хендлер на команду /start
@fp.handler.on_message(text='/start')
async def start_dialog(message: Message, state: FSMContext):
    await message.answer("Привет! Для выдачи товара введи свой игровой никнейм:")
    # Включаем состояние ожидания ника
    await state.set_state(States.wait_for_nickname)

# Хендлер обрабатывает сообщения, ТОЛЬКО если у юзера стейт 'wait_for_nickname'
@fp.handler.on_message(state=States.wait_for_nickname)
async def process_nickname(message: Message, state: FSMContext):
    # Сохраняем введенный ник во временные данные контекста
    await state.update_data(nickname=message.text)
    await message.answer(f"Отлично, я запомнил ник {message.text}.\nТеперь напиши 'да' для подтверждения:")
    # Переводим на следующий шаг
    await state.set_state(States.wait_for_confirm)

# Финальный шаг
@fp.handler.on_message(state=States.wait_for_confirm)
async def process_confirm(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        # Достаем ранее сохраненные данные
        user_data = await state.get_data()
        saved_nick = user_data.get("nickname")
        
        await message.answer(f"Выдача на ник {saved_nick} успешно завершена!")
        # Очищаем стейт и данные, возвращая чат в дефолтное состояние
        await state.clear_state()
    else:
        await message.answer("Пожалуйста, напиши 'да' для подтверждения или начни заново.")</code></pre>

<hr>

<h2>📚 3. Справочник методов FSMContext (Шпаргалка)</h2>

<p>Эти асинхронные методы доступны у объекта <code>state</code>, который вы принимаете аргументом в хендлерах.</p>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
  <thead>
    <tr style="background-color: rgba(0,176,255,0.1); border-bottom: 2px solid #00b0ff;">
      <th style="padding: 10px; text-align: left; width: 25%;">Метод</th>
      <th style="padding: 10px; text-align: left; width: 25%;">Что принимает</th>
      <th style="padding: 10px; text-align: left; width: 20%;">Что возвращает</th>
      <th style="padding: 10px; text-align: left; width: 30%;">Краткое описание</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await state.set_state()</code></td>
      <td style="padding: 10px;"><code>state: str | None</code></td>
      <td style="padding: 10px;"><code>None</code></td>
      <td>Устанавливает текущее состояние для чата. Если передать <code>None</code>, стейт сотрется.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await state.get_state()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><code>str | None</code></td>
      <td>Возвращает строковое название текущего состояния чата. Если состояния нет — вернет <code>None</code>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await state.update_data()</code></td>
      <td style="padding: 10px;"><code>**kwargs</code> (именованные аргументы)</td>
      <td style="padding: 10px;"><code>None</code></td>
      <td>Сохраняет или обновляет временные данные внутри контекста (например: <code>balance=500, step=2</code>).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await state.get_data()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><code>dict</code></td>
      <td>Возвращает словарь со всеми сохраненными временными данными этого чата.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await state.clear_state()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><code>None</code></td>
      <td>Полностью очищает состояние и удаляет все связанные временные данные из хранилища.</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🔧 4. Создание кастомного хранилища (Для продвинутых)</h2>

<p>Если вам нужно, чтобы стейты сохранялись даже после перезапуска бота (например, в базу данных Redis, SQLite или PostgreSQL), вы можете унаследовать свой класс от <code>BaseStorage</code> и переопределить ключевые методы:</p>

<pre><code class="language-python">from fpx.fsm import BaseStorage

class AsyncSqliteStorage(BaseStorage):
    async def set_state(self, chat_id: str, state: str | None):
        # Ваша логика записи стейта в БД
        pass

    async def get_state(self, chat_id: str) -> str | None:
        # Ваша логика чтения стейта из БД
        pass
        
    # И так далее для update_data, get_data и clear_state</code></pre>