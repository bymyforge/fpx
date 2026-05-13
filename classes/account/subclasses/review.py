from models.account import Review
'''
СДЕЛАТЬ ФУНКЦИИ ПРОСМОТРА ОТЗЫВОВ, ОТВЕТА НА ОТЗЫВ(хотя через ордер дата можно получить инфу о отзыве, завтра надо разобратся)
'''


class ReviewManager:
    def __init__(self, account):
        self.account = account

    async def get_review(self, order_id):
        r = await self.account.order.get_order_details(order_id)
        rev = r.review
        review = Review(text=rev.get('text'), stars=rev.get('stars'))
        return review