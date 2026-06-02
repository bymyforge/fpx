


class CategoryRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_lot_category_cache(self, lot_category_ids):
        new_cache = []
        for category_id in lot_category_ids:
            lot = await self.runner._account.category.get_lot_category_last_lot(category_id)
            new_cache.append(lot)
        self.runner._cache['old_lot_categories'] = self.runner._cache['lot_categories']
        self.runner._cache['lot_categories'] = new_cache

    async def _update_chip_category_cache(self, chip_category_ids):
        new_cache = []
        for category_id in chip_category_ids:
            lot = await self.runner._account.category.get_chip_category_last_lot(category_id)
            new_cache.append(lot)
        self.runner._cache['old_chip_categories'] = self.runner._cache['chip_categories']
        self.runner._cache['chip_categories'] = new_cache

    async def _compare_lot_category_cache(self):
        result = []
        if self.runner._cache['lot_categories'] != self.runner._cache['old_lot_categories']:
            for lot in self.runner._cache['lot_categories']:
                if lot not in self.runner._cache['old_lot_categories']:
                    result.append(lot)
        return result

    async def _compare_chip_category_cache(self):
        result = []
        if self.runner._cache['chip_categories'] != self.runner._cache['old_chip_categories']:
            for lot in self.runner._cache['chip_categories']:
                if lot not in self.runner._cache['old_chip_categories']:
                    result.append(lot)
        return result

    async def _check_lot_categories(self, lot_category_ids):
        await self._update_lot_category_cache(lot_category_ids)
        lots = await self._compare_lot_category_cache()
        if lots:
            for lot in lots:
                for handler in self.runner.handler._handlers['lot_category']:
                    await handler(lot)

    async def _check_chip_categories(self, chip_category_ids):
        await self._update_chip_category_cache(chip_category_ids)
        lots = await self._compare_chip_category_cache()
        if lots:
            for lot in lots:
                for handler in self.runner.handler._handlers['chip_category']:
                    await handler(lot)
