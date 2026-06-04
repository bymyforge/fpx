<h1 align="center">✉️ Работа с чатами и сообщениями</h1>

<p>В этом разделе описано, как принимать входящие сообщения, фильтровать их и отправлять ответы пользователям через различные компоненты фреймворка.</p>

<hr>

<h2>📥 1. Перехват сообщений (Хендлеры)</h2>

<p>Для отслеживания новых сообщений в реальном времени используется декоратор <code>@fp.handler.on_message()</code>. Диспетчер автоматически слушает лонгпулл и вызывает функции, когда кто-то пишет боту.</p>

<pre><code class="language-python">@fp.handler.on_message()
async def handle_any_message(message: Message):
    # Сработает абсолютно на любое текстовое сообщение
    await message.answer("Я получил твое сообщение!")</code></pre>

<h3>Фильтрация сообщений</h3>
<p>Вы можете ограничить срабатывание хендлера, передавая параметры прямо в декоратор:</p>

<ul>
  <li><code>text</code> - текст на который начинается сообщение.</li>
  <li><code>mapping</code> - словарь с командой и ответом на эту команду (пример: {'/start': 'Привет, я на связи', 'Ку-ку': 'Кукареку'})
  <li><code>state</code> - проверка текущего состояния FSM (подробнее в разделе Машина состояний).</li>
</ul>

<pre><code class="language-python"># Сработает только если пользователь начал сообщение с "Привет"
@fp.handler.on_message(text="Привет")
async def hello_handler(message: Message):
    await message.answer("И тебе привет")</code></pre>

<hr>

<h2>📦 2. Объект Message и быстрые ответы</h2>

<p>Когда срабатывает хендлер, в него прилетает объект класса <code>Message</code>, содержащий всю информацию о событии:</p>

<ul>
  <li><code>message.text</code> - текст сообщения (строка).</li>
  <li><code>message.chat_id</code> - уникальный цифровой идентификатор чата.</li>
  <li><code>message.is_system</code> - системное ли сообщение (True/False).</li>
  <li><code>message.sender</code> - никнейм отправителя на FunPay.</li>
</ul>

<p>Самый простой способ ответить пользователю - использовать встроенный асинхронный метод <code>message.answer()</code>, которому нужен только текст:</p>
<pre><code class="language-python">await message.answer("Текст вашего ответа покупателю")</code></pre>

<hr>

<h2>⚙️ 3. Продвинутое управление чатами (Runner / Account)</h2>

<p>Если вам нужно выполнить действие с чатом вне хендлера (например, отправить сообщение по расписанию, подгрузить историю или проверить список диалогов), используйте методы из подсистем <code>account.chat</code>.</p>

<h3>Отправка сообщения по ID чата</h3>
<p>Если у вас есть только цифровой ID чата (например, сохраненный в базу данных), вы можете отправить туда текст напрямую:</p>

<pre><code class="language-python"># Через подсистему account
await fp.account.chat.send_message(chat_id=1234567, text="Привет! Это автоматическое уведомление.")</code></pre>

<h3>Получение списка чатов и истории</h3>

<pre><code class="language-python"># Получить список последних 20 чатов с аккаунта
recent_chats = await fp.account.chat.get_chats()

for chat in recent_chats:
    print(f"Чат с пользователем {chat.username} (ID: {chat.id})")

# Получить историю сообщений конкретного чата
history = await fp.account.chat.get_chat_data(chat_id=1234567)</code></pre>

<hr>

<h2>📚 Справочник методов</h2>

<p>Быстрый список всех доступных методов и декораторов для работы с сообщениями и чатами. Сохраните себе, чтобы не искать по всей документации.</p>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
  <thead>
    <tr style="background-color: rgba(0,176,255,0.1); border-bottom: 2px solid #00b0ff;">
      <th style="padding: 10px; text-align: left; width: 25%;">Компонент / Метод</th>
      <th style="padding: 10px; text-align: left; width: 20%;">Что принимает</th>
      <th style="padding: 10px; text-align: left; width: 20%;">Что возвращает</th>
      <th style="padding: 10px; text-align: left; width: 35%;">Краткое описание</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>@fp.handler.on_message()</code></td>
      <td style="padding: 10px;"><code>text: str</code><br><code>mapping: dict</code><br><code>state: str</code></td>
      <td style="padding: 10px;"><a href="models/#Message"><code>Message</code></a> (в хендлер)</td>
      <td>Декоратор для перехвата сообщений. Передает в функцию объект <code>Message</code> с данными чата, отправителя и методом <code>.answer()</code>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await message.answer()</code></td>
      <td style="padding: 10px;"><code>text: str</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Быстрый асинхронный ответ в тот же чат, откуда пришло сообщение. Поддерживает автоформатирование. Возвращает <code>True</code> при успехе.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.chat.send_message()</code></td>
      <td style="padding: 10px;"><code>chat_id: str</code><br><code>text: str</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Отправляет текстовое сообщение в чат по его ID. Возвращает <code>True</code>, если отправлено успешно. Вызывает ошибку, если доставить не удалось.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.chat.get_chats()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><a href='models/#Chat'><code>list[Chat]</code></td>
      <td>Собирает все чаты на аккаунте. Возвращает список объектов с ID, юзернеймом, текстом и датой последнего сообщения, ссылкой и флагом прочтения.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.chat.get_chat_data()</code></td>
      <td style="padding: 10px;"><code>chat_id: int | str</code></td>
      <td style="padding: 10px;"><a href="models/#ChatData"><code>ChatData</code></a></td>
      <td>Скачивает технические данные чата. Возвращает объект <code>ChatData</code> (node_name, csrf_token, user_id, last_message) и сохраняет токены в кэш.</td>
    </tr>
  </tbody>
</table>

<div class="admonition tip" style="padding: 15px; border-left: 5px solid #00e676; background-color: rgba(0,230,118,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #00e676;">💡 Совет по разработке</p>
  <p>Все методы, начинающиеся с <code>await</code>, являются асинхронными - обязательно вызывайте их с ключевым словом <code>await</code> внутри ваших <code>async def</code> функций.</p>
</div>