from authzed.api.v1 import Relationship, ObjectReference, SubjectReference


def make_owner_relationship(project_num: int, user_index: list[int] | int, object_type: str = None) -> Relationship:
    object_type = object_type or "project"
    user_index = user_index[0] if type(user_index) is list else user_index
    return Relationship(
        resource=ObjectReference(object_type=object_type, object_id=str(project_num)),
        relation="owner",
        subject=SubjectReference(
            object=ObjectReference(object_type="user", object_id=str(user_index))
        ),
    )


def make_project_relationship(project_num: int, group_index: int) -> Relationship:
    return Relationship(
        resource=ObjectReference(
            object_type="project",
            object_id=str(project_num)
        ),
        relation="resource_pool_group",
        subject=SubjectReference(
            object=ObjectReference(
                object_type="resource_pool_group",
                object_id=str(group_index)
            )
        ),
    )