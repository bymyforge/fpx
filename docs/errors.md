<h1 align="center">⚠️ Обработка ошибок (Исключения)</h1>

<p>В этом разделе собраны все встроенные исключения фреймворка. Архитектура ошибок построена по трехслойной иерархии, что позволяет гибко перехватывать как конкретные баги (например, неотправленное сообщение), так и целые группы сбоев одним блоком <code>except</code>.</p>

<hr>

<h2>🌳 1. Дерево исключений</h2>

<p>Смотри, как устроена вложенность классов. Каждый дочерний эксепшен наследует поведение своего родителя:</p>

<pre><code class="language-text">FpxError (Базовый класс для всего фреймворка)
 ├── FpxAccountError (Сбои действий аккаунта)
 │    ├── FpxMessageDeliverError (Сообщение не ушло)
 │    ├── FpxRaisingLotError (Нечего или не удалось поднять)
 │    ├── FpxRefundError (Косяк с возвратом денег)
 │    ├── FpxRequestError (Сеть легла / таймаут запроса)
 │    ├── FpxLotEditingError (Цена на сайте не применилась)
 │    ├── FpxAnswerReviewError (Ответ на отзыв не сохранился)
 │    └── FpxClientNotAttachedError (Объект не привязан к клиенту)
 │
 ├── FpxParseError (Проблемы с чтением страниц)
 │    └── FpxNullDataError (Пришел пустой скелет вместо данных)
 │
 └── FpxRunnerError (Проблемы фонового движка)
      └── FpxCriticalRunnerError (Критический сбой, движок остановлен)</code></pre>

<hr>

<h2>💻 2. Примеры обработки ошибок</h2>

<h3>Пример А. Перехват конкретной ошибки (Хороший тон)</h3>
<p>Если мы пишем скрипт демпинга цен, разумно ловить именно <code>FpxLotEditingError</code>, чтобы в случае неудачи сделать повторную попытку через время.</p>

<pre><code class="language-python">from fpx.utils.errors import FpxLotEditingError
import asyncio

try:
    await fp.account.lot_editor.change_lot_price(lot_id=12345, new_price="100.00")
except FpxLotEditingError as e:
    print(f"❌ Не удалось изменить цену лота: {e.message}")
    # Тут можно вызвать логгер или повторить запрос</code></pre>

<h3>Пример Б. Групповой перехват сетевых косяков</h3>
<p>Если тебе неважно, что именно пошло не так в запросах к FunPay (упал ли сервер, или не отправилось сообщение) — лови родительский класс <code>FpxAccountError</code>.</p>

<pre><code class="language-python">from fpx.utils.errors import FpxAccountError

try:
    await message.answer("Вот твой купленный товар!")
except FpxAccountError as e:
    print(f"🚨 Ошибка при работе с API FunPay: {e.message}")</code></pre>

<hr>

<h2>📚 3. Полный справочник исключений</h2>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
  <thead>
    <tr style="background-color: rgba(255,82,82,0.1); border-bottom: 2px solid #ff5252;">
      <th style="padding: 10px; text-align: left; width: 30%;">Класс исключения</th>
      <th style="padding: 10px; text-align: left; width: 30%;">Родительский класс</th>
      <th style="padding: 10px; text-align: left; width: 40%;">Когда вызывается</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxError</code></td>
      <td style="padding: 10px;"><code>Exception</code></td>
      <td>Абсолютный корень всех ошибок фреймворка. Поймает вообще любой баг внутри либы.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td style="padding: 10px;"><code>FpxError</code></td>
      <td>Базовый класс для любых действий аккаунта (запросы, заказы, чаты, лоты).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxParseError</code></td>
      <td style="padding: 10px;"><code>FpxError</code></td>
      <td>Базовый класс для ошибок парсинга данных. Сигнализирует об изменении верстки сайта.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxRunnerError</code></td>
      <td style="padding: 10px;"><code>FpxError</code></td>
      <td>Базовый класс для ошибок фонового раннера лонгпулла.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxMessageDeliverError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Вызывается, если отправленное текстовое сообщение не было успешно доставлено в чат.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxRaisingLotError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Вызывается при неудачном автоподнятии лотов (например, если у аккаунта вообще нет активных позиций).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxRefundError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Возникает при ошибке возврата средств покупателю за заказ.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxRequestError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Превышено количество попыток запроса, пропал интернет или сервера FunPay полностью легли.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxLotEditingError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Вызывается редактором лотов, если после изменения цены проверка на сайте показала старую цену.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxAnswerReviewError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Возникает, если официальный ответ под отзывом в профиле не сохранился или сервер прислал пустой JSON.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxClientNotAttachedError</code></td>
      <td style="padding: 10px;"><code>FpxAccountError</code></td>
      <td>Объект контекста не привязан к главному клиенту fpx и не имеет прав выполнять асинхронные запросы.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxNullDataError</code></td>
      <td style="padding: 10px;"><code>FpxParseError</code></td>
      <td>Парсер ожидал вытянуть данные, но веб-страница вернула пустые теги или базовый скелет (проверь куки/сессию).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>FpxCriticalRunnerError</code></td>
      <td style="padding: 10px;"><code>FpxRunnerError</code></td>
      <td>Критический внутренний сбой фонового процесса проверок, требующий полной остановки или жесткого рестарта скрипта.</td>
    </tr>
  </tbody>
</table>