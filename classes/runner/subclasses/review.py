




class ReviewRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_review_cache(self):
        '''Обновляет кеш отзывов'''
        profile = await self.runner._account.profile.profile()
        self.runner._cache['old_reviews'] = self.runner._cache['reviews']
        self.runner._cache['reviews'] = profile.reviews

    async def _compare_review_cache(self):
        '''Сравнивает кеш отзывов'''
        result = []
        if self.runner._cache['reviews'] != self.runner._cache['old_reviews']:
            for review in self.runner._cache['reviews']:
                if review not in self.runner._cache['old_reviews']:
                    result.append(review)
        return result

    async def _check_reviews(self):
        await self.runner._review._update_review_cache()
        reviews = await self.runner._review._compare_review_cache()
        if reviews:
            for handler in self.runner.handler._handlers['review']:
                await handler(reviews)