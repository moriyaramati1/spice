from authzed.api.v1 import RelationshipFilter
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from spicedb_test.client import spicedb_client as client_spice
from db.base import Base

from db.utils import make_owner_relationship


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    responsible_team: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)


    @property
    def owners(self):
        response = client_spice.ReadRelationships(
            RelationshipFilter(
                resource_type="project",
                optional_resource_id=str(self.id),
                optional_relation="owner",
            )
        )

        owner_ids = []

        for rel in response:
            owner_ids.append(int(rel.relationship.subject.object.object_id))

        return owner_ids

    @owners.setter
    def owners(self, value: list[int]):
        relations = []
        for owner in value:
            relations.append(make_owner_relationship(self.id, owner))

        client_spice.ImportBulkRelationships(relations)



