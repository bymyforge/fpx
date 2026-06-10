import asyncio
from fpx import FunPayTools, CurReview

async def main():
    fp = FunPayTools('YOUR_GOLDEN_KEY')

    @fp.router.on_new_review(stars=1)
    @fp.router.on_new_review(stars=2)
    @fp.router.on_new_review(stars=3)
    async def handle_review(review: CurReview):
        print(f"[REVIEW] {review.stars}★ от {review.author}: {review.text}")
        await review.message_author("Извините за неудобства. Давайте решим проблему.")
        print("[REVIEW] Ответ на негативный отзыв отправлен.")

    await fp.runner.start_polling(3, is_background=True)
    await fp.runner.idle()

if __name__ == '__main__':
    asyncio.run(main())