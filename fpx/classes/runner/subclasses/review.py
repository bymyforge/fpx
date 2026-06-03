
from fpx.models.account import CurReview, Order



class ReviewRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_review_cache(self):
        '''Обновляет кеш отзывов'''
        profile = await self.runner._account.profile.profile()
        self.runner._cache['old_reviews'] = self.runner._cache['reviews'].copy()
        self.runner._cache['reviews'] = profile.reviews

    async def _compare_review_cache(self):
        '''Сравнивает кеш отзывов'''
        result = []
        old_ids = {r.order_id for r in self.runner._cache['old_reviews'] if r.order_id}
        for review in self.runner._cache['reviews']:
            if review.order_id not in old_ids:
                result.append(review)
        return result

    async def _target_review_processing(self, review: CurReview):
        order = await self.runner._account.order.get_order_details(review.order_id)
        review._client = self.runner
        review.order = order
        for handler in self.runner.handler._handlers['review']:
            await handler(review)

    async def _check_reviews(self):
        await self.runner._review._update_review_cache()
        reviews = await self.runner._review._compare_review_cache()
        if reviews:
            for review in reviews:
                await self._target_review_processing(review)