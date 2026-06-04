<h1 align="center">👤 Управление профилем и балансом</h1>

<p>В этом разделе описано, как получать технические данные аккаунта (ID, CSRF-токены), запрашивать текущий баланс в разных валютах, парсить выставленные лоты, отзывы и общую историю продаж через подсистему <code>account.profile</code>.</p>

<hr>

<h2>💻 1. Примеры использования</h2>

<p>Все методы для работы с профилем вызываются через компонент <code>fp.account.profile</code>. При первом вызове фреймворк автоматически кэширует сессионные токены, так что вручную за этим следить не нужно.</p>

<h3>Пример А. Проверка баланса аккаунта</h3>
<p>Метод <code>get_balance()</code> возвращает удобный объект, разделенный по трем основным валютам на FunPay.</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools

fp = FunPayTools("ВАШ_GOLDEN_KEY")

async def check_my_money():
    # Запрашиваем состояние кошелька
    balance = await fp.account.profile.get_balance()
    
    print(f"💰 Баланс в рублях: {balance.rub} ₽")
    print(f"💵 Баланс в долларах: {balance.usd} $")
    print(f"💶 Баланс в евро: {balance.eur} €")

async def main():
    await check_my_money()

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<h3>Пример Б. Получение отзывов из профиля</h3>
<p>Вы можете спарсить последние отзывы со страницы своего (или чужого) профиля, чтобы, например, выводить их в консоль или анализировать фидбек.</p>

<pre><code class="language-python">async def show_reviews():
    # Если user_id не передан, метод автоматически узнает ID владельца сессии
    my_profile = await fp.account.profile.profile()
    
    print(f"Найдено категорий с лотами: {len(my_profile.category_ids)}")
    print("Последние отзывы в профиле:")
    
    for review in my_profile.reviews:
        print(f"[{review.stars}/5 ⭐] {review.author}: {review.text}")</code></pre>

<hr>

<h2>📚 2. Справочник методов API (Шпаргалка)</h2>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
  <thead>
    <tr style="background-color: rgba(0,176,255,0.1); border-bottom: 2px solid #00b0ff;">
      <th style="padding: 10px; text-align: left; width: 25%;">Компонент / Метод</th>
      <th style="padding: 10px; text-align: left; width: 20%;">What принимает</th>
      <th style="padding: 10px; text-align: left; width: 20%;">What возвращает</th>
      <th style="padding: 10px; text-align: left; width: 35%;">Краткое описание</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.profile.get_user_data()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><a href="models/#UserData"><code>UserData</code></a></td>
      <td>Парсит главное меню FunPay. Узнает ваш никнейм, ID и закидывает актуальный CSRF-токен в кэш для будущих POST-запросов.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.profile.get_my_sells()</code></td>
      <td style="padding: 10px;"><code>limit: int</code> (дефолт 0)</td>
      <td style="padding: 10px;"><code>list[<a href="models/#Order">Order</a>]</code></td>
      <td>Запрашивает и парсит всю страницу ваших продаж. Если <code>limit=0</code>, вернет вообще все заказы, иначе — строго указанное количество.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.profile.profile()</code></td>
      <td style="padding: 10px;"><code>user_id: str | int</code> (опционально)</td>
      <td style="padding: 10px;"><a href="models/#Profile"><code>Profile</code></a></td>
      <td>Загружает публичную страницу профиля пользователя. Находит ID активных категорий, список лотов и последние отзывы.</td>
    </tr>
    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
      <td style="padding: 10px;"><code>await fp.account.profile.get_balance()</code></td>
      <td style="padding: 10px;"><i>нет</i></td>
      <td style="padding: 10px;"><a href="models/#Balance"><code>Balance</code></a></td>
      <td>Парсит финансовую страницу FunPay и вытягивает чистый баланс аккаунта отдельно для RUB, USD и EUR.</td>
    </tr>
  </tbody>
</table>

<div class="admonition info" style="padding: 15px; border-left: 5px solid #00b0ff; background-color: rgba(0,176,255,0.1); margin-top: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #00b0ff;">💡 Важная деталь про get_my_sells</p>
  <p>Этот метод возвращает список стандартных объектов <code>Order</code>. Вы можете использовать полученные данные для анализа старых заказов (проверить статус, ник клиента, цену), но помните, что у архивных заказов из этого списка методы быстрых ответов <code>.answer()</code> вызывать нельзя, так как они не привязаны к активному лонгпуллу раннера.</p>
</div>