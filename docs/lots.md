<h1 align="center">🛍 Работа с лотами и автоподнятие</h1>

<p>В этом разделе описано, как получать информацию о ваших товарах, настраивать автоматическое поднятие лотов в топ выдачи, а также динамически редактировать цены и статус позиций.</p>

<hr>

<h2>📋 1. Получение инфы и автоподнятие (LotManager)</h2>

<p>Все методы для анализа и поднятия лотов находятся в компоненте <code>fp.account.lot</code>.</p>

<h3>Пример: Скрипт для бесконечного автоподнятия лотов</h3>
<p>Метод <code>raise_lots()</code> автоматически собирает все категории, в которых у вас есть товары, и отправляет запросы на их поднятие. За завернутый цикл с задержкой ваш аккаунт будет всегда висеть в топе.</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools

fp = FunPayTools("ВАШ_GOLDEN_KEY")

async def auto_raise_loop():
    while True:
        try:
            print("Отправляем запрос на поднятие лотов...")
            responses = await fp.account.lot.raise_lots()
            print(f"Успешно подняли категории! Получено ответов: {len(responses)}")
        except Exception as e:
            print(f"Ошибка при поднятии: {e}")
            
        # FunPay разрешает поднимать лоты раз в 2-4 часа. Ставим задержку в 30 минут.
        await asyncio.sleep(60 * 30)

async def main():
    # Запускаем автоподнятие фоном
    asyncio.create_task(auto_raise_loop())
    # Запускаем самого раннера
    await fp.runner.start_polling(3)
    await fp.runner.idle()

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<hr>

<h2>📚 2. Справочник методов API (Шпаргалка)</h2>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
  <thead>
    <tr style="background-color: rgba(0,176,255,0.1); border-bottom: 2px solid #00b0ff;">
      <th style="padding: 10px; text-align: left; width: 30%;">Компонент / Метод</th>
      <th style="padding: 10px; text-align: left; width: 20%;">Что принимает</th>
      <th style="padding: 10px; text-align: left; width: 20%;">Что возвращает</th>
      <th style="padding: 10px; text-align: left; width: 30%;">Краткое описание</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot.get_lot_info()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code></td>
      <td style="padding: 10px;"><a href="models/#CurrentLotInfo"><code>CurrentLotInfo</code></a></td>
      <td>Собирает текущие данные лота с сайта (короткое/полное описание, цену).</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot.raise_lots()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><code>list</code></td>
      <td>Поднимает абсолютно все ваши лоты во всех доступных категориях. Если нечего поднимать, вызовет <code>FpxRaisingLotError</code>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot_editor.change_lot_price()</code></td>
      <td style="padding: 10px;"><code>lot_id</code>, <code>new_price: str</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Меняет цену товара. Делает паузу 0.5с для валидации результата. При ошибке кидает <code>FpxLotEditingError</code>.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot_editor.toggle_off_lot()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Выключает (деактивирует) лот, убирая его из поиска маркетплейса.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.lot_editor.toggle_on_lot()</code></td>
      <td style="padding: 10px;"><code>lot_id: str | int</code></td>
      <td style="padding: 10px;"><code>bool</code></td>
      <td>Активирует лот, возвращая его на витрину FunPay.</td>
    </tr>
  </tbody>
</table>

<div class="admonition info" style="padding: 15px; border-left: 5px solid #00b0ff; background-color: rgba(0,176,255,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #00b0ff;">ℹ️ Скрытые методы</p>
  <p>Метод <code>_get_lot_editor_details()</code> возвращает технический объект <a href="models.md#LotEditor"><code>LotEditor</code></a> с полным слепком полей формы и CSRF-токеном. Он используется подкапотно и не рекомендуется для вызова в обычной логике ботов.</p>
</div>