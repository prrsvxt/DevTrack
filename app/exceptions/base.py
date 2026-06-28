class AppError(Exception):
    pass


class NotFoundError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


class ConflictError(AppError):
    pass


class BusinessRuleError(AppError):
    pass

class BadRequestError(AppError):
    pass