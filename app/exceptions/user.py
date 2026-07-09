from app.exceptions.base import AppError, ConflictError


class UserAlreadyExistsError(ConflictError):
    pass


class UsernameAlreadyTakenError(ConflictError):
    pass


class InvalidCredentialsError(AppError):
    pass
