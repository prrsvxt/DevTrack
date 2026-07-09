from app.exceptions.base import BadRequestError, NotFoundError, PermissionDeniedError


class TaskNotFoundError(NotFoundError):
    pass


class TaskPermissionError(PermissionDeniedError):
    pass


class InvalidPaginationError(BadRequestError):
    pass
