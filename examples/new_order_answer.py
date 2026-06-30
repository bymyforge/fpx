import asyncio

from fpx import FunPayTools, types


async def main():
    fp = FunPayTools('YOUR_GOLDEN_KEY', 'YOUR_GOLDEN_SEAL')

    @fp.router.on_new_order()
    async def greet_new_order(order: types.Order):
        print(f"[ORDER] Новый заказ #{order.order_id} от {order.client_name}")

        # Отправляем сообщение в чат заказа
        await order.answer(
            f'Привет, {order.client_name}!\n'
            f'Заказ "{order.name}" принят. Ожидайте доставку!'
        )

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())
