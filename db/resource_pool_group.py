from authzed.api.v1 import RelationshipFilter
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spicedb_test.client import spicedb_client as client_spice
from db.base import Base
from db.utils import make_project_relationship


class ResourcePoolGroup(Base):
    __tablename__ = "resource_pool_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    _project_id: Mapped[int | None] = mapped_column("project_id", Integer, nullable=True)

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

    @property
    def project_id(self) -> int | None:
        return self._project_id

    @project_id.setter
    def project_id(self, value: int  | None) -> None:

        # If no change → do nothing
        if value == self._project_id:
            return

        old_value = self._project_id
        self._project_id = value

        # ID must exist before writing to SpiceDB
        if not self.id:
            return

        # -------------------------
        # DELETE OLD RELATION
        # -------------------------
        if old_value is not None:
            client_spice.DeleteRelationships(
                RelationshipFilter(
                    resource_type="resource_pool_group",
                    optional_resource_id=str(self.id),
                    optional_relation="project",
                )
            )

        # -------------------------
        # ADD NEW RELATION
        # -------------------------
        if value is not None:
            relation = make_project_relationship(value, self.id)

            client_spice.ImportBulkRelationships([relation])