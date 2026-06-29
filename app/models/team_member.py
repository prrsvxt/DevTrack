from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint, Enum
from datetime import datetime

from app.db.base import Base
from app.enums.team_role import TeamRole


class TeamMember(Base):
    __tablename__ = 'team_members'

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    team: Mapped['Team'] = relationship(back_populates='team_members')
    user: Mapped['User'] = relationship(back_populates='team_members')
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole, name='team_role'), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name="uq_team_member"),
    )