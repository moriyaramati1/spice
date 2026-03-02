from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.project_owners import project_owners


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)

    owned_projects: Mapped[list["Project"]] = relationship(
        secondary=project_owners,
        back_populates="owners",
    )