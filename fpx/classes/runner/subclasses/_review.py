import asyncio
import logging
import inspect

from fpx.models.account import CurReview, Order

logger = logging.getLogger("fpx.review_runner")

class ReviewRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_review_cache(self):
        '''Обновляет кеш отзывов'''
        profile = await self.runner._account.profile.profile()
        self.runner._cache['old_reviews'] = self.runner._cache.get('reviews', [])
        self.runner._cache['reviews'] = profile.reviews

    def _compare_review_cache(self):
        '''Сравнивает кеш отзывов'''
        result = []
        old_ids = {r.order_id for r in self.runner._cache['old_reviews'] if r.order_id}
        for review in self.runner._cache['reviews']:
            if review.order_id not in old_ids:
                result.append(review)
        return result

    async def _target_review_processing(self, review: CurReview):
        try:
            order = await self.runner._account.order.get_order_details(review.order_id)
            review._client = self.runner
            review.order = order
            for handler in self.runner.router._handlers['review']:
                if handler['stars'] is None:
                    await self.runner.router.invoke(handler['function'], review)
                else:
                    if review.stars == handler['stars']:
                        await self.runner.router.invoke(handler['function'], review)
        except Exception as e:
            logger.debug(f'В процессе обработки отзыва произошла ошибка: {e}. Убедитесь что всё хорошо', exc_info=True)
            await self.runner._handle_error(event=review, exception=e)

    async def _check_reviews(self):
        await self._update_review_cache()
        reviews = self._compare_review_cache()
        if reviews:
            tasks = [self._target_review_processing(review) for review in reviews]
            await asyncio.gather(*tasks)