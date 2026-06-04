<h1 align="center">📊 Мониторинг рынка и Демпинг</h1>

<p>В этом разделе описано, как отслеживать цены конкурентов в реальном времени. С помощью подсистемы <code>account.category</code> вы можете ловить моменты, когда кто-то снижает цену в категории, и автоматически перебивать её, чтобы ваш лот всегда оставался на первом месте в выдаче.</p>

<hr>

<h2>📥 1. Отслеживание конкурентов (Хендлеры)</h2>

<p>Фреймворк разделяет категории на два типа: обычные лоты (аккаунты, ключи, услуги) и чипсы (игровая валюта с быстрой формой заказа). Хендлеры автоматически игнорируют изменения ваших собственных цен, реагируя только на конкурентов.</p>

<h3>Пример: Автоматический демпинг (Удержание топ-1)</h3>
<p>Смотри, как легко связать мониторинг категории с редактором лотов, чтобы автоматически снижать цену на 0.1 ₽, когда конкурент пытается нас обогнать:</p>

<pre><code class="language-python">from fpx import FunPayTools, CategoryLastLot

fp = FunPayTools("ВАШ_GOLDEN_KEY")

# Указываем ID лота, который мы хотим защищать
MY_LOT_ID = 11223344

# Хендлер сработает, если в отслеживаемой категории лотов изменился топ-1
@fp.handler.on_lot_category()
async def auto_dumping(lot: CategoryLastLot):
    print(f"🔥 Конкурент {lot.owner_username} перебил цену! Текущий топ-1: {lot.price} ₽")
    
    # Рассчитываем новую цену (на 10 копеек дешевле конкурента)
    target_price = round(lot.price - 0.1, 2)
    
    # Меняем цену своего лота через редактор
    await fp.account.lot_editor.change_lot_price(lot_id=MY_LOT_ID, new_price=str(target_price))
    print(f"✅ Успешно перебили цену! Наша новая цена: {target_price} ₽")</code></pre>

<hr>

<h2>⚙️ 2. Сбор данных вручную (CategoryManager)</h2>

<p>Если вам не нужен постоянный фоновый мониторинг, вы можете в любой момент запросить самый дешевый лот по каждому из фильтров категории в коде программы через компонент <code>fp.account.category</code>.</p>

<pre><code class="language-python"># Получить топ-1 лот по всем фильтрам в категории (например, категория "Скины CS2")
top_lots = await fp.account.category.get_lot_category_last_lot(lot_category_id=123)
for lot in top_lots:
    print(f"Фильтр: {lot.filtration} | Самый дешевый: {lot.price} ₽ от {lot.owner_username}")</code></pre>

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
      <td style="padding: 10px;"><code>@fp.handler.on_lot_category()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><a href="models/#CategoryLastLot"><code>CategoryLastLot</code></a> (в хендлер)</td>
      <td>Декоратор отслеживает снижение цен или смену топ-лота в категориях <b>обычных лотов</b>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>@fp.handler.on_chip_category()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><a href="models/#CategoryLastLot"><code>CategoryLastLot</code></a> (в хендлер)</td>
      <td>Декоратор отслеживает снижение цен в категориях <b>«чипсов» (игровой валюты)</b>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.category.get_lot_category_last_lot()</code></td>
      <td style="padding: 10px;"><code>lot_category_id: int | str</code></td>
      <td style="padding: 10px;"><code>list[<a href="models/#CategoryLastLot">CategoryLastLot</a>]</code></td>
      <td>Находит самые дешевые предложения в указанной категории лотов по каждому из доступных фильтров.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.category.get_chip_category_last_lot()</code></td>
      <td style="padding: 10px;"><code>chip_category_id: int | str</code></td>
      <td style="padding: 10px;"><code>list[<a href="models/#CategoryLastLot">CategoryLastLot</a>]</code></td>
      <td>Находит самые дешевые предложения в указанной категории игровой валюты («чипсов») по каждому из фильтров.</td>
    </tr>
  </tbody>
</table>

<div class="admonition warning" style="padding: 15px; border-left: 5px solid #ff5252; background-color: rgba(255,82,82,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #ff5252;">⚠️ Обрати внимание на аргументы методов</p>
  <p>В методе <code>get_chip_category_last_lot</code> аргумент называется <code>chip_category_id</code>, но он выполняет ту же роль, что и <code>lot_category_id</code> в параллельном методе — принимает ID целевой категории для парсинга.</p>
</div>