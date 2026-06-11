import asyncio
import logging
import inspect

from fpx.models.account import CurReview, Order
from fpx.utils.dependencies import Dependency

logger = logging.getLogger("fpx.review_runner")

class ReviewRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_review_cache(self):
        '''Обновляет кеш отзывов'''
        profile = await self.runner._account.profile.profile()
        self.runner._cache['old_reviews'] = self.runner._cache.get('reviews', [])
        self.runner._cache['reviews'] = profile.reviews

    async def _compare_review_cache(self):
        '''Сравнивает кеш отзывов'''
        result = []
        old_ids = {r.order_id for r in self.runner._cache['old_reviews'] if r.order_id}
        for review in self.runner._cache['reviews']:
            if review.order_id not in old_ids:
                result.append(review)
        return result

    async def _call_handler(self, h_func, review):
                    sig = inspect.signature(h_func)
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if param.annotation == CurReview or param_name == 'review':
                            kwargs[param_name] = review
                            continue
                        if isinstance(param.default, Dependency):
                            dep_func = param.default.dependency
                            if asyncio.iscoroutinefunction(dep_func):
                                kwargs[param_name] = await dep_func(review)
                            else:
                                kwargs[param_name] = dep_func(review)
                    await h_func(**kwargs)

    async def _target_review_processing(self, review: CurReview):
        try:
            order = await self.runner._account.order.get_order_details(review.order_id)
            review._client = self.runner
            review.order = order
            for handler in self.runner.router._handlers['review']:
                if handler['stars'] is None:
                    await self._call_handler(handler['function'], review)
                else:
                    if review.stars == handler['stars']:
                        await self._call_handler(handler['function'], review)
        except Exception as e:
            logger.debug(f'В процессе обработки отзыва произошла ошибка: {e}. Убедитесь что всё хорошо')
            await self.runner._handle_error(event=message, exception=e)

    async def _check_reviews(self):
        await self.runner._review._update_review_cache()
        reviews = await self.runner._review._compare_review_cache()
        if reviews:
            tasks = [self._target_review_processing(review) for review in reviews]
            await asyncio.gather(*tasks)