from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.base import Base
from db.project_owners import project_owners


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    responsible_team: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)

    owners: Mapped[list["User"]] = relationship(
        secondary=project_owners,
        back_populates="owned_projects",
    )
