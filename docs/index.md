<h1 align="center">🚀 fpx-engine</h1>

<p align="center">
  <em>Ультимативный асинхронный фреймворк на Python для полной автоматизации и создания ботов на маркетплейсе FunPay.</em>
</p>

<p align="center">
  <a href="https://github.com/bymyforge/fpx" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="https://t.me/fpx_engine" target="_blank">
    <img src="https://img.shields.io/badge/Телеграм_Чат-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>
  <a href="https://pypi.org/project/fpx-engine/" target="_blank">
    <img src="https://img.shields.io/badge/PyPI-3775A9?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/fpx-engine?color=blue&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
</p>

<hr>

<h2>🔥 Почему fpx-engine?</h2>

<p><code>fpx-engine</code> - полноценный фреймворк с понятной архитектурой и целью максимально упростить взаимодействие разработчика с фанпей. Фреймворк очень похож на <code>aiogram</code>, если вы уже писали на нём, вы почувствуете себя как дома.</p>

<ul>
  <li><b>🚀 Полная асинхронность:</b> Построен на базе современных библиотек.</li>
  <li><b>⚡️ Простота взаимодействия: Изначальная цель библиотеки максимально упростить жизнь разработчику.</li>
</ul>

<hr>

<h2>⚠️ КРИТИЧЕСКАЯ ИНФОРМАЦИЯ (ПРОЧИТАТЬ ПЕРЕД ЗАПУСКОМ!)</h2>

<div class="admonition danger" style="padding: 15px; border-left: 5px solid #ff5252; background-color: rgba(255,82,82,0.1); margin-bottom: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #ff5252;">🛑 Безопасность вашего аккаунта (Golden Key)</p>
  <p>Фреймворк использует ваш <code>golden_key</code> для авторизации запросов к API FunPay.</p>
  <ul>
    <li><b>НИКОГДА</b> не выкладывайте файлы конфигурации или <code>.env</code> файлы с вашим ключом в открытые репозитории на GitHub!</li>
    <li><b>Помните:</b> Получив ваш <code>golden_key</code>, злоумышленник получает <b>полный доступ</b> к вашему аккаунту, включая вывод средств и управление лотами. Используйте переменные окружения.</li>
  </ul>
</div>

<div class="admonition warning" style="padding: 15px; border-left: 5px solid #ffb300; background-color: rgba(255,179,0,0.1); margin-bottom: 20px;">
  <p style="margin-top: 0; font-weight: bold; color: #ffb300;">⚠️ Риски блокировки и лимиты</p>
  <p>FunPay активно борется с агрессивным парсингом. Чтобы ваш аккаунт жил долго и счастливо:</p>
  <ul>
    <li>Не выставляйте задержку обновления кэша заказов и лонгпулла сообщений ниже <b>1-2 секунд</b>. Слишком частый спам запросами гарантированно приведет к временному или перманентному бану со стороны Cloudflare/FunPay.</li>
    <li>По возможности используйте качественные прокси, если запускаете несколько аккаунтов одновременно.</li>
  </ul>
</div>

<hr>

<h2>🛠 Быстрая установка</h2>

<p>Установка стандартная через менеджер пакетов <code>pip</code>:</p>

<pre><code class="language-bash">pip install fpx-engine --upgrade</code></pre>

<hr>

<h2>💻 Минимальный пример эхо бота</h2>

<p>Вот как выглядит простейший бот, который будет автоматически отвечать на любые входящие сообщения:</p>

<pre><code class="language-python">import asyncio
from fpx import FunPayTools, Message

# Инициализируем клиент
fp = FunPayTools("ВАШ_GOLDEN_KEY")

@fp.handler.on_message()
async def echo_handler(message: Message):
    # Бот просто вернет текст пользователя обратно в чат
    await message.answer(f"Вы написали: {message.text}")

async def main():
    # Запускаем бесконечный цикл прослушивания событий
    await fp.runner.start_polling()

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<hr>

<h2>🧭 Куда идти дальше?</h2>

<p>Для детального изучения фреймворка используйте навигацию или переходите по ссылкам ниже:</p>

<ul>
  <li><a href="quickstart/"><b>🚀 Быстрый старт</b></a> - Полноценная настройка проекта, авторизация и первый запуск.</li>
  <li><a href="chat/"><b>✉️ Обработка сообщений</b></a> - Фильтры, маппинг триггеров и автоответы.</li>
  <li><a href="orders/"><b>📦 Работа с заказами</b></a> - Как ловить оплату, проверять статусы и выдавать товар.</li>
  <li><a href="fsm/"><b>🧠 Машина состояний (FSM)</b></a> - Создание сложных пошаговых сценариев (сбор ников/паролей и тп.) через <code>FSMContext</code>.</li>
</ul>