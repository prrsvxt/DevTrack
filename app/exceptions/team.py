from app.exceptions.base import NotFoundError, PermissionDeniedError


class TeamNotFoundError(NotFoundError):
    pass


class TeamPermissionError(PermissionDeniedError):
    pass