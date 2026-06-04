<h1 align="center">⭐️ Работа с отзывами</h1>

<p>В этом разделе описано, как перехватывать новые отзывы в реальном времени, фильтровать их по количеству звезд, отправлять официальные ответы на страницу профиля или писать автору отзыва в чат.</p>

<hr>

<h2>📥 1. Отслеживание отзывов (Хендлеры)</h2>

<p>Для отслеживания новых отзывов используется декоратор <code>@fp.handler.on_new_review()</code>. Вы можете настроить бота так, чтобы он реагировал вообще на все отзывы, либо только на определенный рейтинг (например, благодарил за 5 звезд и звал саппорт при 1 звезде).</p>

<h3>Пример: Автоматический ответ на отзывы</h3>
<p>В объект <code>CurReview</code>, который прилетает в функцию, фреймворк автоматически подтягивает данные заказа. Метод <code>review.answer()</code> поддерживает плейсхолдеры для красивого форматирования текста.</p>

<pre><code class="language-python"># Хендлер сработает только если покупатель оставил 5 звезд
@fp.handler.on_new_review(stars=5)
async def поблагодарить_за_отзыв(review: CurReview):
    # Отправляем официальный ответ под отзыв в профиле
    # Переменные {author} и {order_name} подставятся автоматически!
    await review.answer("Спасибо за покупку, {author}! Рады, что вам понравился {order_name}!")
    print(f"Ответили на 5-звездочный отзыв от {review.author}")

# Хендлер для плохих отзывов (1-3 звезды)
@fp.handler.on_new_review(stars=1)
@fp.handler.on_new_review(stars=2)
@fp.handler.on_new_review(stars=3)
async def решить_проблему(review: CurReview):
    # Пишем клиенту напрямую в чат заказа, чтобы помочь
    await review.message_author("Здравствуйте, {author}. Почему вы оставили {stars} звезд? Давайте решим проблему в этом чате!")
</code></pre>

<hr>

<h2>⚙️ 2. Работа с отзывами вне хендлеров (ReviewManager)</h2>

<p>Если вам нужно получить или ответить на отзыв конкретного заказа по его ID (например, в админ-панели), используйте прямые методы из подсистемы <code>fp.account.review</code>.</p>

<pre><code class="language-python"># Запросить данные отзыва для конкретного заказа
review_info = await fp.account.review.get_review(order_id="📥 ID_ЗАКАЗА")
print(f"Текст отзыва: {review_info.text} | Наш ответ: {review_info.answer}")

# Оставить ответ на отзыв вручную
await fp.account.review.review_answer(order_id="📥 ID_ЗАКАЗА", text="Спасибо за ваш фидбек!")</code></pre>

<hr>

<h2>📚 3. Справочник методов API (Шпаргалка)</h2>

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
      <td style="padding: 10px;"><code>@fp.handler.on_new_review()</code></td>
      <td style="padding: 10px;"><code>stars: int | None</code></td>
      <td style="padding: 10px;"><a href="models/#CurReview"><code>CurReview</code></a> (в хендлер)</td>
      <td>Декоратор для перехвата новых отзывов. Если <code>stars</code> не передан, ловит вообще все отзывы.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.review.get_review()</code></td>
      <td style="padding: 10px;"><code>order_id: str | int</code></td>
      <td style="padding: 10px;"><a href="models/#Review"><code>Review</code></a></td>
      <td>Запрашивает информацию об отзыве, привязанном к конкретному ID заказа.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.review.review_answer()</code></td>
      <td style="padding: 10px;"><code>order_id: str | int</code><br><code>text: str</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Публикует официальный ответ на отзыв. Бросает <code>FpxAnswerReviewError</code>, если ответ не сохранился или сервер лежит.</td>
    </tr>
  </tbody>
</table>

<div class="admonition info" style="padding: 15px; border-left: 5px solid #00b0ff; background-color: rgba(0,176,255,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #00b0ff;">💡 В чем разница между Review и CurReview?</p>
  <p>Объект <a href="models.md#Review"><code>Review</code></a> — это просто сухие архивные данные (текст, звезды, ответ). Объект <a href="models.md#CurReview"><code>CurReview</code></a> прилетает в хендлеры живого лонгпулла, он содержит ссылку на полный объект заказа и снабжен методами <code>.answer()</code> и <code>.message_author()</code> для быстрой автоматизации действий.</p>
</div>