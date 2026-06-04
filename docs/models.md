<h1 align="center">📦 Модели и Типы данных</h1>

<p>В этом разделе описана структура всех основных датаклассов (моделей), которые возвращают методы и хендлеры фреймворка <code>fpx-engine</code>. Вы можете использовать их поля для реализации гибкой логики ваших ботов.</p>

<hr>

<div id="Message" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(0,176,255,0.2); border-radius: 8px; background-color: rgba(0,176,255,0.02);">
  <h2 style="margin-top: 0; color: #00b0ff;">📋 Класс Message</h2>
  <p>Объект перехватываемого входящего сообщения. Прилетает основным аргументом в хендлер <code>@fp.handler.on_message()</code>.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>sender</code> (str) - Имя (никнейм) отправителя сообщения.</li>
    <li><code>chat_id</code> (str) - Уникальный идентификатор чата (node id переписки).</li>
    <li><code>text</code> (str) - Текст входящего сообщения.</li>
    <li><code>is_system</code> (bool) - Флаг: <code>True</code>, если сообщение является системным уведомлением FunPay.</li>
  </ul>

  <h3>Методы объекта:</h3>
  <ul>
    <li><code>await message.answer(answer_text: str)</code> - Асинхронный ответ в этот же чат. Возвращает <code>bool</code>.
      <br><small style="color: #888;">💡 Поддерживает автоматическое форматирование текста. В строку ответа можно подставлять переменные: <code>{sender}</code>, <code>{chat_id}</code>, <code>{text}</code>.</small>
    </li>
  </ul>
</div>

<hr>

<div id="Order" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(160,82,255,0.2); border-radius: 8px; background-color: rgba(160,82,255,0.02);">
  <h2 style="margin-top: 0; color: #b052ff;">📦 Класс Order</h2>
  <p>Объект с подробной информацией о заказе. Передается в хендлеры событий заказов или возвращается методом <code>get_order_details()</code>.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>order_id</code> (str | None) - Уникальный ID заказа на FunPay.</li>
    <li><code>chat_id</code> (str | None) - ID чата, привязанного к этому заказу.</li>
    <li><code>order_time</code> (str | None) - Время оплаты/оформления заказа.</li>
    <li><code>description</code> (str | None) - Подробное описание заказа (данные лота, которые оставил покупатель при покупке).</li>
    <li><code>client_name</code> (str | None) - Никнейм покупателя.</li>
    <li><code>price</code> (float | None) - Стоимость заказа в виде числа.</li>
    <li><code>status</code> (str | None) - Текущий статус ("Оплачено", "Закрыт", "Возврат" и т.д.).</li>
    <li><code>name</code> (str | None) - Название купленного товара / лота.</li>
    <li><code>category</code> (str | None) - Категория товара на маркетплейсе.</li>
    <li><code>review</code> (dict | None) - Словарь с данными отзыва к заказу, если он оставлен.</li>
  </ul>

  <h3>Методы объекта:</h3>
  <ul>
    <li><code>await order.answer(answer_text: str)</code> - Быстро отправить сообщение в чат этого заказа покупателю. Возвращает <code>bool</code>.
      <br><small style="color: #888;">💡 Поддерживает автоматическое форматирование. Доступны теги: <code>{order_id}</code>, <code>{order_time}</code>, <code>{client_name}</code>, <code>{order_name}</code>.</small>
    </li>
  </ul>
</div>

<hr>

<div id="CurReview" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(255,179,0,0.2); border-radius: 8px; background-color: rgba(255,179,0,0.02);">
  <h2 style="margin-top: 0; color: #ffb300;">⭐️ Класс CurReview</h2>
  <p>Объект текущего отзыва на вашем аккаунте. Позволяет автоматизировать работу со входящим фидбеком от покупателей.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>text</code> (str) - Текст отзыва, оставленный покупателем.</li>
    <li><code>stars</code> (int) - Количество звезд (оценка от 1 до 5).</li>
    <li><code>author</code> (str) - Никнейм покупателя, оставившего отзыв.</li>
    <li><code>order_id</code> (str) - ID заказа, к которому привязан отзыв.</li>
    <li><code>order</code> (<a href="#Order"><code>Order</code></a> | None) - Ссылка на связанный объект заказа, если он подгружен.</li>
  </ul>

  <h3>Методы объекта:</h3>
  <ul>
    <li><code>await cur_review.answer(answer_text: str)</code> - Оставить официальный ответ под отзывом на странице профиля. Возвращает <code>bool</code>.
      <br><small style="color: #888;">💡 Поддерживает плейсхолдеры: <code>{author}</code>, <code>{order_id}</code>, <code>{order_name}</code>, <code>{order_time}</code>.</small>
    </li>
    <li><code>await cur_review.message_author(message_text: str)</code> - Написать автору отзыва напрямую в личные сообщения (в чат заказа). Возвращает <code>bool</code>.
      <br><small style="color: #888;">💡 Поддерживает те же плейсхолдеры для подстановки данных.</small>
    </li>
  </ul>
</div>

<hr>

<div id="ChatData" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(0,230,118,0.2); border-radius: 8px; background-color: rgba(0,230,118,0.02);">
  <h2 style="margin-top: 0; color: #00e676;">⚙️ Класс ChatData</h2>
  <p>Технические данные конкретной переписки. Возвращается при детальном запросе информации о чате.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>node_name</code> (str) - Строковый системный идентификатор комнаты (например: <code>users-12345-67890</code>), необходимый для отправки POST-запросов сообщений.</li>
    <li><code>csrf_token</code> (str) - Актуальный CSRF-токен веб-сессии.</li>
    <li><code>user_id</code> (str) - Ваш собственный цифровой ID аккаунта.</li>
    <li><code>last_message</code> (list) - Список/структура с информацией о последнем сообщении в чате.</li>
  </ul>
</div>

<hr>

<div id="CategoryLastLot" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(255,82,82,0.2); border-radius: 8px; background-color: rgba(255,82,82,0.02);">
  <h2 style="margin-top: 0; color: #ff5252;">📊 Класс CategoryLastLot</h2>
  <p>Объект, содержащий информацию о последнем лоте в определенной категории. Используется для мониторинга рынка и цен конкурентов.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>category_id</code> (str) - ID отслеживаемой категории FunPay.</li>
    <li><code>filtration</code> (str) - Примененные параметры фильтрации на странице.</li>
    <li><code>price</code> (float) - Актуальная цена лота.</li>
    <li><code>offer_id</code> (str) - Уникальный ID конкретного торгового предложения.</li>
    <li><code>owner_username</code> (str) - Никнейм продавца, которому принадлежит этот лот.</li>
  </ul>
</div>

<hr>

<div id="CurrentLotInfo" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(0,176,255,0.2); border-radius: 8px; background-color: rgba(0,176,255,0.02);">
  <h2 style="margin-top: 0; color: #00b0ff;">🛍 Класс CurrentLotInfo</h2>
  <p>Краткая информация о текущем состоянии вашего лота/оффера.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>short_desc</code> (str) - Короткое описание лота, видимое в общем списке категории.</li>
    <li><code>description</code> (str) - Полный текст описания внутри карточки товара.</li>
    <li><code>price</code> (float) - Выставленная стоимость лота.</li>
  </ul>
</div>

<hr>

<div id="UserData" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(136,136,136,0.2); border-radius: 8px; background-color: rgba(136,136,136,0.02);">
  <h2 style="margin-top: 0; color: #aaaaaa;">🔑 Класс UserData</h2>
  <p>Техническая информация о сессии авторизованного пользователя.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>csrf_token</code> (str) - Кросс-сайтовый токен безопасности текущей сессии для отправки POST-запросов к FunPay.</li>
    <li><code>user_id</code> (str) - Цифровой уникальный ID вашего профиля.</li>
  </ul>
</div>

<hr>

<div id="Profile" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(244,67,54,0.2); border-radius: 8px; background-color: rgba(244,67,54,0.02);">
  <h2 style="margin-top: 0; color: #f44336;">👤 Класс Profile</h2>
  <p>Полный слепок данных вашего профиля FunPay.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>category_ids</code> (list) - Список ID категорий, в которых у вас есть активные или созданные лоты.</li>
    <li><code>lots</code> (list[LotInfo]) - Список объектов созданных вами лотов (содержит названия и их ID).</li>
    <li><code>reviews</code> (list[<a href="#CurReview"><code>CurReview</code></a>]) - Список объектов последних отзывов, оставленных на вашем аккаунте.</li>
  </ul>
</div>

<hr>

<div id="Review" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(158,158,158,0.2); border-radius: 8px; background-color: rgba(158,158,158,0.02);">
  <h2 style="margin-top: 0; color: #9e9e9e;">💬 Класс Review</h2>
  <p>Упрощенный статический объект отзыва (архивные данные/история).</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>text</code> (str) - Текст самого отзыва от покупателя.</li>
    <li><code>stars</code> (int) - Оценка в звездах (1-5).</li>
    <li><code>answer</code> (str) - Текст вашего ответа на этот отзыв (если вы на него отвечали).</li>
  </ul>
</div>

<hr>

<div id="Balance" style="margin-bottom: 40px; padding: 20px; border: 1px solid rgba(0,230,118,0.2); border-radius: 8px; background-color: rgba(0,230,118,0.02);">
  <h2 style="margin-top: 0; color: #00e676;">💰 Класс Balance</h2>
  <p>Объект с балансом вашего кошелька, разбитый по трем основным доступным на маркетплейсе валютам. Возвращается методом <code>await fp.account.profile.get_balance()</code>.</p>
  
  <h3>Доступные поля:</h3>
  <ul>
    <li><code>rub</code> (float) - Доступный баланс в российских рублях.</li>
    <li><code>usd</code> (float) - Доступный баланс в долларах США.</li>
    <li><code>eur</code> (float) - Доступный баланс в евро.</li>
  </ul>
</div>