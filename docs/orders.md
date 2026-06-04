<h1 align="center">📦 Работа с заказами</h1>

<p>В этом разделе описано, как отслеживать новые оплаты, подтверждения и возвраты заказов, а также управлять ими через подсистему <code>account.order</code>.</p>

<hr>

<h2>📥 1. Отслеживание заказов (Хендлеры)</h2>

<p>Фреймворк предоставляет 4 декоратора для гибкого перехвата событий. Во все хендлеры заказов можно вторым аргументом передавать <code>state: FSMContext</code> - магия диспетчера автоматически свяжет его с чатом этого заказа.</p>

<div class="admonition warning" style="padding: 15px; border-left: 5px solid #ffb300; background-color: rgba(255,179,0,0.1); margin-bottom: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #ffb300;">⚠️ Важно избежать дублирования</p>
  <p>Не рекомендуется использовать общий декоратор <code>on_orders()</code> одновременно с узкопрофильными (например, <code>on_new_order()</code>), иначе одно и то же событие обработается дважды.</p>
</div>

<h3>Пример: Автовыдача товара при новой оплате</h3>
<p>Срабатывает, когда покупатель оплатил заказ и ждет товар. Хендлер проверяет ключевые слова в описании лота через параметр <code>mapping</code>.</p>

<pre><code class="language-python"># Бот сработает только если в описании купленного товара есть "ключ" или "key"
@fp.handler.on_new_order(mapping=["ключ", "key"])
async def auto_delivery(order: Order, state: FSMContext):
    # Отправляем товар в чат этого заказа
    await order.answer("Спасибо за покупку! Вот твой ключ: XXXXX-YYYYY-ZZZZZ")
    print(f"Успешно выдали товар для заказа #{order.order_id}")</code></pre>

<hr>

<h2>📚 2. Справочник методов API (Шпаргалка)</h2>

<p>Сухой список всех декораторов и методов менеджера заказов.</p>

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
      <td style="padding: 10px;"><code>@fp.handler.on_orders()</code></td>
      <td style="padding: 10px;"><code>mapping: list[str]</code></td>
      <td style="padding: 10px;"><a href="models/#Order"><code>Order</code></a> (в хендлер)</td>
      <td>Отслеживает <b>абсолютно все</b> изменения и статусы заказов (оплата, подтверждение, возврат).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>@fp.handler.on_new_order()</code></td>
      <td style="padding: 10px;"><code>mapping: list[str]</code></td>
      <td style="padding: 10px;"><a href="models/#Order"><code>Order</code></a> (в хендлер)</td>
      <td>Срабатывает только на появление <b>новых оплаченных</b> заказов, требующих выдачи.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>@fp.handler.on_confirmed_orders()</code></td>
      <td style="padding: 10px;"><code>mapping: list[str]</code></td>
      <td style="padding: 10px;"><a href="models/#Order"><code>Order</code></a> (в хендлер)</td>
      <td>Ловит событие <b>подтверждения заказа</b> (когда покупатель нажал кнопку "Подтвердить выполнение").</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>@fp.handler.on_refunded_orders()</code></td>
      <td style="padding: 10px;"><code>mapping: list[str]</code></td>
      <td style="padding: 10px;"><a href="models/#Order"><code>Order</code></a> (в хендлер)</td>
      <td>Отслеживает события <b>возврата средств</b> по заказу.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.order.get_order_details()</code></td>
      <td style="padding: 10px;"><code>order_id: str | int</code></td>
      <td style="padding: 10px;"><a href="models/#Order"><code>Order</code></a></td>
      <td>Запрашивает полную инфу о заказе с его веб-страницы (включая отзывы, описание и chat_id).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.order.refund_order()</code></td>
      <td style="padding: 10px;"><code>order_id: str | int</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Делает принудительный возврат денег покупателю. Возвращает <code>True</code> при успехе, иначе бросает <code>FpxRefundError</code>.</td>
    </tr>
  </tbody>
</table>