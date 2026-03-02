from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from db.base import Base


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    responsible_team: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True
                                                  )
    owners: Mapped[list[id]] = mapped_column(ForeignKey("user.id"), nullable=True)
