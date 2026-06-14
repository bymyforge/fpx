import asyncio
from fpx import FunPayTools, Message, CurReview, Order

CATEGORY_TO_WATCH = 1316

async def main():
    fp = FunPayTools('YOUR_GOLDEN_KEY')

    # ─── Старт ───
    @fp.router.on_startup()
    async def startup():
        print("[BOT] Запускаюсь...")
        balance = await fp.account.profile.get_balance()
        print(f"[BOT] Баланс: {balance.rub}₽")

    # ─── Сообщения ───
    @fp.router.on_message()
    async def chat_handler(message: Message):
        print(f"[MSG] {message.sender}: {message.text}")
        if message.is_system:
            return
        await message.answer("Сообщение получено, скоро отвечу!")

    # ─── Новые заказы ───
    @fp.router.on_new_order()
    async def new_order(order: Order):
        print(f"[ORDER] Новый: #{order.order_id} — {order.name}")
        await order.answer(f'Спасибо за заказ "{order.name}"! Начинаю выполнение.')

    # ─── Подтверждённые заказы ───
    @fp.router.on_confirmed_orders()
    async def confirmed(order: Order):
        print(f"[CONFIRM] Заказ #{order.order_id} подтверждён!")
        await order.answer("Заказ выполнен! Буду рад отзыву ⭐")

    # ─── Отзывы ───
    @fp.router.on_new_review(stars=5)
    async def review_handler(review: CurReview):
        print(f"[REVIEW] {review.stars}★: {review.text}")
        await review.answer("Спасибо за отзыв! ❤️")
        await review.message_author("Спасибо за отзыв! ❤️")

    # ─── Ошибки ───
    @fp.router.on_error()
    async def error_handler(event, exception):
        print(f"[ERROR] Произошла ошибка: {exception}")

    # ─── Запуск ───
    await fp.runner.start_polling(
        3,
        is_background=True,
        watch_lots=[CATEGORY_TO_WATCH]
    )
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())