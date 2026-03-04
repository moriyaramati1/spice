from authzed.api.v1 import RelationshipFilter
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spicedb_test.client import spicedb_client as client_spice, spicedb_client
from db.base import Base
from db.utils import make_project_relationship


class ResourcePoolGroup(Base):
    __tablename__ = "resource_pool_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    _project_id: Mapped[int | None] = mapped_column("project_id", Integer, nullable=True)

    # self-referencing FK (tree)
    _parent_resource_pool_group_id: Mapped[int | None] = mapped_column(
        "parent_resource_pool_group_id",
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

    @property
    def parent_resource_pool_group_id(self) -> int | None:
        return self._parent_resource_pool_group_id

    @parent_resource_pool_group_id.setter
    def parent_resource_pool_group_id(self, new_parent_id: int | None):

        old_parent_id = self._parent_resource_pool_group_id

        # If nothing changed → do nothing
        if old_parent_id == new_parent_id:
            return

        # Remove old relation in SpiceDB
        if old_parent_id is not None and self.id is not None:
            spicedb_client.delete_relationship(
                resource_type="resource_pool_group",
                resource_id=str(self.id),
                relation="parent",
                subject_type="resource_pool_group",
                subject_id=str(old_parent_id),
            )

        # Update DB value
        self._parent_resource_pool_group_id = new_parent_id

        # Add new relation in SpiceDB
        if new_parent_id is not None and self.id is not None:
            spicedb_client.write_relationship(
                resource_type="resource_pool_group",
                resource_id=str(self.id),
                relation="parent",
                subject_type="resource_pool_group",
                subject_id=str(new_parent_id),
            )