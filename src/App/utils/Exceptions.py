class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnauthorizedError(Exception):
    def __init__(self, message):
        super().__init__(message)
