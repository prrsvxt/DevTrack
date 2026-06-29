from app.exceptions.base import ConflictError, PermissionDeniedError, NotFoundError


class TeamMemberAlreadyExistsError(ConflictError):
    pass

class TeamMemberPermissionError(PermissionDeniedError):
    pass

class TeamMemberNotFoundError(NotFoundError):
    pass