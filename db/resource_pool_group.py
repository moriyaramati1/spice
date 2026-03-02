from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class ResourcePoolGroup(Base):
    __tablename__ = "resource_pool_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    project_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # self-referencing FK (tree)
    parent_resource_pool_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("resource_pool_group.id"),
        nullable=True,
    )

    # ORM relationships
    parent: Mapped["ResourcePoolGroup | None"] = relationship(
        back_populates="children",
        remote_side="ResourcePoolGroup.id",
    )

    children: Mapped[list["ResourcePoolGroup"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )