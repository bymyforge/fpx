<h1 align="center">🚀 Быстрый старт</h1>

<p>В этом руководстве мы разберем, как поднять вашего первого асинхронного бота на <code>fpx-engine</code> за 5 минут.</p>

<hr>

<h2>🔑 Шаг 1. Получение Golden Key (Токена сессии)</h2>

<p>Для работы с API FunPay фреймворку необходим ваш уникальный ключ авторизации - <code>golden_key</code>. Он вытаскивается прямо из ваших куков браузера.</p>

<ol>
  <li>Откройте официальный сайт <b>FunPay</b> в браузере и убедитесь, что вы вошли в свой аккаунт.</li>
  <li>Нажмите клавишу <code>F12</code> (или правая кнопка мыши -> <i>Посмотреть код / Исследовать элемент</i>), чтобы открыть панель разработчика.</li>
  <li>Перейдите во вкладку <b>Application</b> (в Chrome/Edge) или <b>Storage</b> (в Firefox).</li>
  <li>В боковом меню разверните пункт <b>Cookies</b> и выберите сайт <code>https://funpay.com</code>.</li>
  <li>Найдите в списке куку с именем <code>golden_key</code> и скопируйте ее значение (длинная строка из букв и цифр).</li>
</ol>

<div class="admonition danger" style="padding: 15px; border-left: 5px solid #ff5252; background-color: rgba(255,82,82,0.1); margin-bottom: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #ff5252;">🛑 ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ</p>
  <p>Ваш <code>golden_key</code> - это ваш пароль и доступ ко всем деньгам на аккаунте. Никогда и ни при каких обстоятельствах не передавайте его третьим лицам и не выкладывайте на GitHub!</p>
</div>

<hr>

<h2>🛠 Шаг 2. Установка фреймворка</h2>

<p>Убедитесь, что у вас установлен Python версии 3.10 или выше, и выполните команду в терминале:</p>

<pre><code class="language-bash">pip install fpx-engine --upgrade</code></pre>

<hr>

<h2>💻 Шаг 3. Примеры простых скриптов</h2>

<p>Выберите нужный вам вариант, создайте файл <code>main.py</code>, вставьте код и замените значение <code>ВАШ_GOLDEN_KEY</code> на скопированную ранее куку.</p>

<h3>Вариант А. Эхо бот</h3>
<p>Этот бот будет мгновенно отвечать на любые входящие сообщения в чате, возвращая текст пользователя обратно.</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools, Message

# Инициализируем бота
fp = FunPayTools("ВАШ_GOLDEN_KEY")

@fp.handler.on_message()
async def handle_message(message: Message):
    # Отправляем зеркальный ответ в этот же чат
    await message.answer(f"Привет! Вы написали: {message.text}")

async def main():
    # Запуск бесконечного прослушивания лонгпулла сообщений
    await fp.runner.start_polling(3)
    await fp.runner.idle()

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<h3>Вариант Б. Базовая автовыдача (Реакция на новый заказ)</h3>
<p>Этот бот автоматически отслеживает новые оплаченные заказы, отправляет покупателю товар/инструкцию в чат.</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools

fp = FunPayTools("ВАШ_GOLDEN_KEY")

# Хендлер сработает только на статус Оплачено
@fp.handler.on_new_order()
async def handle_new_buy(order: Order):
    print(f"Обнаружен новый заказ #{order.order_id}!")
    
    # Отправляем сообщение в чат этого заказа
    await order.answer("Спасибо за покупку! Вот ваши данные: Секретный_Товар_123")

async def main():
    await fp.runner.start_polling()

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<hr>

<h2>🏃 Шаг 4. Запуск бота</h2>
<p>Запустите созданный файл через ваш терминал:</p>
<pre><code class="language-bash">python main.py</code></pre>
<p>Попробуйте написать своему боту с другого аккаунта или совершить тестовую покупку - бот мгновенно отработает логику в фоновом режиме!</p>