import random
from datetime import datetime
from main import spice_handler
from authzed.api.v1 import InsecureClient, WriteSchemaRequest, SubjectReference
from authzed.api.v1.permission_service_pb2 import ImportBulkRelationshipsRequest, CheckBulkPermissionsRequestItem, \
    CheckBulkPermissionsRequest, CheckPermissionResponse

client_spice = spice_handler.client

schema = """
    definition user {}
    definition usergroup {
        relation direct_member: user

        permission member = direct_member
    }

    definition resource_pool_group {
        relation owner: user
        relation can_edit: user

        permission direct_permission = owner
        permission can_edit_permission = owner + can_edit
    }

    definition project {
        relation resource_pool_group: resource_pool_group
        relation owner: user
        relation editor: user 

        // Logical link (not used for lookup)

        // Runtime permission
        permission edit = owner + editor
    }

"""



import asyncio
from authzed.api.v1 import Client, ObjectReference, Relationship

NUM_PROJECTS = 180_000  # total projects
NUM_GROUPS = 50  # resource_pool_groups
NUM_USERS = 500  # number of users to assign as owners
GROUP_PREFIX = "rpg_"
USER_PREFIX = "user_"
BATCH_SIZE = 5000  # relationships per request batch


# --- HELPERS ---
def project_id(n: int) -> str:
    return f"project_{n:06d}"


def group_id(n: int) -> str:
    return f"{GROUP_PREFIX}{n:03d}"


def user_id(n: int) -> str:
    return f"{USER_PREFIX}{n:03d}"


def make_relationship(project_num: int, group_index: int) -> Relationship:
    return Relationship(
        resource=ObjectReference(
            object_type="project",
            object_id=project_id(project_num)
        ),
        relation="resource_pool_group",
        subject=SubjectReference(
            object=ObjectReference(
                object_type="resource_pool_group",
                object_id=group_id(group_index)
            )
        ),
    )


def make_owner_relationship(project_num: int, user_index: int, object_type: str = None) -> Relationship:
    object_type = object_type or "project"
    return Relationship(
        resource=ObjectReference(object_type=object_type, object_id=project_id(project_num)),
        relation="owner",
        subject=SubjectReference(
            object=ObjectReference(object_type="user", object_id=user_id(user_index))
        ),
    )


def make_owner_relationship_root_rpg() -> Relationship:
    return Relationship(
        resource=ObjectReference(object_type="resource_pool_group", object_id=group_id(322614)),
        relation="owner",
        subject=SubjectReference(
            object=ObjectReference(object_type="user", object_id=user_id(322615))
        ),
    )


def request_iterator():
    # yield ImportBulkRelationshipsRequest(relationships=[make_owner_relationship_root_rpg()])
    for batch_start in range(1, 150000):
        relationships = []
        if batch_start != 322615:
            relationships.append(make_owner_relationship(batch_start, 322615))
        # relationships.append(make_relationship(batch_start, batch_start))
        # relationships.append(make_owner_relationship(batch_start, batch_start))
        # relationships.append(make_relationship(batch_start, 322614))

        yield ImportBulkRelationshipsRequest(relationships=relationships)
        # print(f"Yielded batch {batch_start}-{batch_end}")


# --- BULK IMPORT ---
async def bulk_import():
    client = client_spice
    # IMPORTANT: pass async generator to ImportBulkRelationships
    response = client.ImportBulkRelationships(request_iterator())
    print(f"Done importing: {response.num_loaded} relationships loaded")



if __name__ == "__main__":
    pass
    # asyncio.run(bulk_import())