import pytest
from unittest.mock import AsyncMock

from app.enums.team_role import TeamRole
from app.exceptions.team_member import TeamMemberAlreadyExistsError, TeamMemberPermissionError
from app.models.team_member import TeamMember
from app.models.user import User
from app.services.team_member_service import TeamMemberService
from app.models.team import Team
from app.models.task import Task

@pytest.fixture
def session():
    return AsyncMock()

@pytest.fixture
def service(session):
    return TeamMemberService(session=session)

@pytest.fixture
def make_user():
    def _make_user(user_id: int = 1) -> User:
        return User(id=user_id)
    return _make_user

@pytest.fixture
def make_member():
    def _make_member(team_id: int = 10, user_id: int = 1, role = TeamRole.OWNER):
        return TeamMember(team_id=team_id, user_id=user_id, role=role)
    return _make_member



@pytest.mark.anyio
async def test_add_existing_member_raises_error(session, service, make_user, make_member):

    current_user = make_user()
    current_member = make_member()
    target_member = make_member(user_id=2, role=TeamRole.DEVELOPER)

    service.team_member_repository.get_by_team_and_user = AsyncMock(side_effect=[current_member, target_member])

    service.team_member_repository.create = AsyncMock()

    with pytest.raises(TeamMemberAlreadyExistsError):
        await service.add_member(team_id=10, target_user_id=2, role=TeamRole.DEVELOPER, current_user=current_user)

    service.team_member_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.anyio
async def test_add_member_success(session, service, make_user, make_member):

    current_user = make_user()

    current_member = make_member()
    created_member = make_member(user_id=2, role=TeamRole.DEVELOPER)

    service.team_member_repository.get_by_team_and_user = AsyncMock(side_effect=[current_member, None])

    service.team_member_repository.create = AsyncMock(return_value=created_member)

    result = await service.add_member(team_id=10, target_user_id=2, role=TeamRole.DEVELOPER, current_user=current_user)

    assert result is created_member

    service.team_member_repository.create.assert_awaited_once_with(team_id=10, user_id=2, role=TeamRole.DEVELOPER)

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(created_member)

@pytest.mark.anyio
async def test_add_owner_role_forbidden(session, service, make_user):

    current_user = make_user()

    with pytest.raises(TeamMemberPermissionError):
        await service.add_member(team_id=10, target_user_id=2, role=TeamRole.OWNER, current_user=current_user)
    
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()

@pytest.mark.anyio
async def test_add_member_without_permission(session, service, make_user, make_member):

    current_user = make_user(user_id=2)
    current_member = make_member(user_id=2, role=TeamRole.DEVELOPER)

    service.team_member_repository.create = AsyncMock()
    service.team_member_repository.get_by_team_and_user = AsyncMock(return_value=current_member)

    with pytest.raises(TeamMemberPermissionError):
        await service.add_member(team_id=10, target_user_id=1, role=TeamRole.VIEWER, current_user=current_user)
    
    service.team_member_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.anyio
async def test_current_user_not_in_team(session, service, make_user):

    current_user = make_user()

    service.team_member_repository.create = AsyncMock()
    service.team_member_repository.get_by_team_and_user = AsyncMock(return_value=None)

    with pytest.raises(TeamMemberPermissionError):
        await service.add_member(team_id=10, target_user_id=2, role=TeamRole.DEVELOPER, current_user=current_user)

    service.team_member_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()
    
@pytest.mark.anyio
async def test_change_member_role_success(session, service, make_user, make_member):

    current_user = make_user()
    current_member = make_member()
    role_changing_member = make_member(user_id=2, role=TeamRole.DEVELOPER)
    member_after_role_changed = make_member(user_id=2, role=TeamRole.VIEWER)

    service.team_member_repository.get_by_team_and_user = AsyncMock(side_effect=[current_member, role_changing_member])
    service.team_member_repository.update_role = AsyncMock(return_value=member_after_role_changed)

    result = await service.change_member_role(team_id=10, target_user_id=2, new_role=TeamRole.VIEWER, current_user=current_user)

    assert result is member_after_role_changed

    service.team_member_repository.update_role.assert_awaited_once_with(role_changing_member, role=TeamRole.VIEWER)

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(member_after_role_changed)


@pytest.mark.anyio
async def test_change_member_role_same_role_returns_member_without_commit(session, service, make_user, make_member):

    current_user = make_user()
    current_member = make_member()
    role_changing_member = make_member(user_id=2, role=TeamRole.DEVELOPER)

    service.team_member_repository.get_by_team_and_user = AsyncMock(side_effect=[current_member, role_changing_member])
    service.team_member_repository.update_role = AsyncMock()

    result = await service.change_member_role(team_id=10, target_user_id=2, new_role=TeamRole.DEVELOPER, current_user=current_user)

    assert result is role_changing_member

    service.team_member_repository.update_role.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.anyio
async def test_not_possible_to_change_owner_role(session, service, make_user, make_member):
    
    current_user = make_user()
    current_member = make_member()
    role_changing_member = make_member(user_id=2)

    service.team_member_repository.get_by_team_and_user = AsyncMock(side_effect=[current_member, role_changing_member])
    service.team_member_repository.update_role = AsyncMock()

    with pytest.raises(TeamMemberPermissionError):
        await service.change_member_role(team_id=10, target_user_id=2, new_role=TeamRole.DESIGNER, current_user=current_user)

    service.team_member_repository.update_role.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()