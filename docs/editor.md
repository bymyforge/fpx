<h1 align="center">🛍 Управление лотами (Editor)</h1>

<p>В этом разделе описано, как динамически управлять вашими торговыми предложениями на FunPay: менять цены на товары, а также временно включать или выключать лоты из выдачи через подсистему <code>account.editor</code>.</p>

<hr>

<h2>💻 1. Примеры использования</h2>

<p>Все методы управления лотами находятся в компоненте <code>fp.account.editor</code>. Для их вызова вам достаточно знать уникальный цифровой ID вашего лота на FunPay.</p>

<h3>Пример А. Автоматическое изменение цены</h3>
<p>Полезно, если вы пишите скрипт для демпинга (автоматического снижения цены, чтобы быть первым в списке конкурентов) или привязываете цены к курсу валют.</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools

fp = FunPayTools("ВАШ_GOLDEN_KEY")

async def main():
    # ID вашего лота можно взять из адресной строки на сайте FunPay
    MY_LOT_ID = 12345678 
    
    print("Изменяем цену лота...")
    # Важно: цену передаем в виде строки!
    success = await fp.account.lot.change_lot_price(lot_id=MY_LOT_ID, new_price="150.50")
    
    if success:
        print("Цена успешно изменена и проверена на сайте!")

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<h3>Пример Б. Выключение лота (Уйти в оффлайн)</h3>
<p>Если у вас закончился товар для автовыдачи, лот нужно временно скрыть, чтобы покупатели не оплачивали пустые заказы.</p>

<pre><code class="language-python">async def деактивировать_товар(lot_id):
    # Лот пропадет из общего списка категорий на FunPay
    await fp.account.lot.toggle_off_lot(lot_id)
    print(f"Лот {lot_id} успешно выключен.")</code></pre>

<hr>

<h2>📚 2. Справочник методов API (Шпаргалка)</h2>

<p>Сухой список всех доступных методов менеджера лотов.</p>

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
      <td style="padding: 10px;"><code>await fp.account.lot.change_lot_price()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code><br><code>new_price: str</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Изменяет цену лота на сайте. Фреймворк делает паузу в 0.5с и перепроверяет, применилась ли цена. Бросает <code>FpxLotEditingError</code> при неуспехе.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot.toggle_off_lot()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Выключает (деактивирует) лот. Товар скрывается из выдачи маркетплейса.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot.toggle_on_lot()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Включает (активирует) лот. Товар снова появляется в общем списке и доступен для покупки.</td>
    </tr>
  </tbody>
</table>

<div class="admonition info" style="padding: 15px; border-left: 5px solid #00b0ff; background-color: rgba(0,176,255,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #00b0ff;">ℹ️ Ошибки при редактировании лотов</p>
  <p>При возникновении проблем с интернетом или если FunPay вернул ошибку, методы могут вызывать исключения <code>FpxRequestError</code> или <code>FpxLotEditingError</code>. Рекомендуется оборачивать вызовы в конструкцию <code>try-except</code>.</p>
</div>