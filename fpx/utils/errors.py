
# Корневой родитель всех ошибок
class FpxError(Exception):
    """Базовое исключение для всего фреймворка."""
    def __init__(self, message='Ошибка вызывана в fpx'):
        self.message = message
        super().__init__(self.message)

# Второй уровень, с сортировкой по группам
class FpxAccountError(FpxError):
    """Ошибки, связанные с действиями аккаунта (запросы, лоты, заказы)."""
    def __init__(self, message='Ошибка аккаунта'):
        super().__init__(message)

class FpxParseError(FpxError):
    """Ошибки парсинга HTML/JSON от фп."""
    def __init__(self, message='Ошибка парсинга данных'):
        super().__init__(message)

class FpxRunnerError(FpxError):
    """Ошибки фонового раннера проверок."""
    def __init__(self, message='Ошибка раннера'):
        super().__init__(message)

class FpxHandlerError(FpxError):
    """Ошибки хендлера."""
    def __init__(self, message='Ошибка раннера'):
        super().__init__(message)

# Третий уровень, конкретные ошибки


# аккаунт
class FpxGetChatsError(FpxAccountError):
    """Не удалось запросить чаты."""
    def __init__(self, message='Не удалось запросить чаты.'):
        super().__init__(message)

class FpxMessageDeliverError(FpxAccountError):
    """Сообщение не было доставлено."""
    def __init__(self, message='Сообщение не было доставлено'):
        super().__init__(message)

class FpxRaisingLotError(FpxAccountError):
    """Ошибка при поднятии лотов."""
    def __init__(self, message='Ошибка при поднятии лотов'):
        super().__init__(message)

class FpxRefundError(FpxAccountError):
    """Ошибка при возврате денег за заказ."""
    def __init__(self, message='Ошибка при возврате денег за заказ'):
        super().__init__(message)

class FpxRequestError(FpxAccountError):
    """Превышено количество попыток запроса или сервер упал."""
    def __init__(self, message='Превышено количество попыток запроса или сервер упал'):
        super().__init__(message)

class FpxLotEditingError(FpxAccountError):
    """Ошибка при редактировании лота."""
    def __init__(self, message='Ошибка при редактировании лота'):
        super().__init__(message)

class FpxAnswerReviewError(FpxAccountError):
    """Ошибка при ответе на отзыв."""
    def __init__(self, message='Ошибка ответа на отзыв'):
        super().__init__(message)

class FpxClientNotAttachedError(FpxAccountError):
    """Объект контекста не привязан к главному клиенту fpx."""
    def __init__(self, message='Объект не привязан к клиенту fpx и не может выполнять действия'):
        super().__init__(message)


# --- Ошибки парсера ---
class FpxNullDataError(FpxParseError):
    """Парсер ожидал данные, но пришёл пустой тег или скелет страницы."""
    def __init__(self, message='Парсер ожидал данные, но пришёл пустой тег или скелет страницы'):
        super().__init__(message)


# --- Ошибки раннера ---
class FpxCriticalRunnerError(FpxRunnerError):
    """Критический сбой раннера, требующий остановки или жесткого перезапуска."""
    def __init__(self, message='Критический сбой раннера, требующий остановки или жесткого перезапуска'):
        super().__init__(message)

# --- Ошибки хендлера ---

class FpxAttributeError(FpxHandlerError):
    """Неправильно переданы аттрибуты."""
    def __init__(self, message='Неправильно переданы аттрибуты'):
        super().__init__(message)

class FpxCommandArgsError(FpxHandlerError):
    """Вызывается, когда функция команды ожидает аргументы, но в сообщении их передали меньше, чем нужно."""
    def __init__(self, function_name, missing_arg):
        self.function_name = function_name
        self.missing_arg = missing_arg
        super().__init__(f"Команда '{function_name}' ожидает аргумент '{missing_arg}', но он не был передан в чате.")