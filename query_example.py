from authzed.api.v1 import CheckBulkPermissionsRequestItem, ObjectReference, SubjectReference, \
    CheckBulkPermissionsRequest, CheckPermissionResponse
from flask_sqlalchemy.session import Session
from sqlalchemy import MetaData, Table, Integer, Column, insert, select
from db.project import Project
from redis_client import redis_client
from spicedb_test.client import spicedb_client


def get_projects(
    session: Session,
    user_id: int,
    object_type: str,
    permission_type,
    page: int = 0,
    name_filter: str | None = None,
    PAGE_SIZE = 10):

    permitted_project_ids: list[int] = list(redis_client.smembers(f"{object_type}:{user_id}:{permission_type}"))
    if not permitted_project_ids:
        return []
    engine = session.get_bind()
    metadata = MetaData()

    permitted_table = Table(
        "#permitted_ids",
        metadata,
        Column("id", Integer, primary_key=True),
    )

    metadata.drop_all(engine, tables=[permitted_table], checkfirst=True)
    metadata.create_all(engine, tables=[permitted_table])

    session.execute(
        insert(permitted_table),
        [{"id": pid} for pid in permitted_project_ids],
    )
    stmt = (
        select(Project)
            .join(permitted_table, Project.id == permitted_table.c.id)
            .order_by(Project.id)
            .offset(page * PAGE_SIZE)
            .limit(PAGE_SIZE)
    )
    if name_filter:
        stmt = stmt.where(Project.name.ilike(f"%{name_filter}%"))
    projects = session.execute(stmt).scalars().all()

    project_ids = [str(p.id) for p in projects]

    allowed_ids = check_projects_permission_batch(
        spicedb_client=spicedb_client,
        user_id=str(user_id),
        project_ids=project_ids,
        permission="view",
    )

    return [p for p in projects if str(p.id) in allowed_ids]





def check_projects_permission_batch(
    spicedb_client,
    user_id: str,
    project_ids: list[str],
    permission: str,
) -> set[str]:

    checks = []
    for project_id in project_ids:
        checks.append(CheckBulkPermissionsRequestItem(resource=ObjectReference(object_id=project_id,
                                                                                    object_type="project"),
                                                           permission=permission,
                                                           subject=SubjectReference(
                                                               object=ObjectReference(object_type="user",
                                                                                      object_id=user_id)
                                                               )))

    request = CheckBulkPermissionsRequest(items=checks)

    results = spicedb_client.client.CheckBulkPermissions(request)
    x = set()
    for result in results.pairs:
        allowed = result.item.permissionship
        if allowed == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION:
            x.add(result.request.resource.object_id)

    return x



# s = time.perf_counter()
# print(time.perf_counter())
# get_projects(db.session, 149,'project','owner')
# y  = time.perf_counter()
# print(y-s)
#
# for batch_start in range(1, 300000):
#         items_spice.append(CheckBulkPermissionsRequestItem(resource=ObjectReference(object_id=project_id(batch_start),
#                                                                                     object_type="project"),
#                                                            permission="edit",
#                                                            subject=SubjectReference(object=ObjectReference(object_type="user",
#                                                            object_id=user_id(322615))
#                                                            )))
#
# print(datetime.now())
# checks = CheckBulkPermissionsRequest(items=items_spice[:9999])
#
# # for result in response.pairs:
# #     allowed = result.item.permissionship
# #     if allowed == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION:
# #         results.append(result.request.resource.object_id)