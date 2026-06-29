from enum import Enum


class TeamRole(str, Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    DEVELOPER = 'developer'
    VIEWER = 'viewer'
    INTERN = 'intern'
    MANAGER = 'manager'
    DESIGNER = 'designer'
    QA = 'qa'