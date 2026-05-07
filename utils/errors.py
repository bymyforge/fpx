



class ParseException(Exception):
    def __init__(self, message='Data parsing error'):
        self.message = message
        super().__init__(self.message)

class NullData(ParseException):
    message = 'Null Data'