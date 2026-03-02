import random
from datetime import datetime

from authzed.api.v1 import InsecureClient, WriteSchemaRequest, SubjectReference
from authzed.api.v1.permission_service_pb2 import ImportBulkRelationshipsRequest, CheckBulkPermissionsRequestItem, \
    CheckBulkPermissionsRequest, CheckPermissionResponse, LookupResourcesRequest, CheckPermissionRequest

import asyncio
from authzed.api.v1 import Client, ObjectReference, Relationship

client = InsecureClient("localhost:50051", "spicy")

NUM_PROJECTS = 180_000       # total projects
NUM_GROUPS = 50              # resource_pool_groups
NUM_USERS = 500              # number of users to assign as owners
GROUP_PREFIX = "rpg_"
USER_PREFIX = "user_"
BATCH_SIZE = 5000            # relationships per request batch

# --- HELPERS ---
def project_id(n: int) -> str:
    return f"project_{n:06d}"

def group_id(n: int) -> str:
    return f"{GROUP_PREFIX}{n:03d}"

def user_id(n: int) -> str:
    return f"{USER_PREFIX}{n:03d}"


def getPermittetProjects():
    items_spice = []
    print(datetime.now())
    for batch_start in range(1, 300000):
            items_spice.append(CheckBulkPermissionsRequestItem(resource=ObjectReference(object_id=project_id(batch_start),
                                                                                        object_type="project"),
                                                               permission="edit",
                                                               subject=SubjectReference(object=ObjectReference(object_type="user",
                                                               object_id=user_id(322615))
                                                               )))

    print(datetime.now())
    checks = CheckBulkPermissionsRequest(items=items_spice[:9999])

    response = client.CheckBulkPermissions(checks)
    print(datetime.now())
    results = []
    for result in response.pairs:
        allowed = result.item.permissionship
        if allowed == CheckPermissionResponse.PERMISSIONSHIP_HAS_PERMISSION:
            results.append(result.request.resource.object_id)

    print(datetime.now())
    print("results", len(set(results)))
    return results

def get_permitted_by_lookup():
    start = datetime.now()
    print(datetime.now())
    request = LookupResourcesRequest(resource_object_type="project",
                                     permission="edit",
                                     subject=SubjectReference(object=ObjectReference(object_type="user", object_id=user_id(322615))))
    count=0
    req_ids = []
    for r in client.LookupResources(request):
        # req_ids.append(r.resource_object_id)
        count += 1
        if count == 100:
            break
    print("first 100 in:", datetime.now() - start)
    print(datetime.now())
    print(len(req_ids))
    return req_ids


if __name__ == "__main__":
    # asyncio.run(bulk_import())
    # print(datetime.now())
    # result = client.CheckPermission(CheckPermissionRequest(resource=ObjectReference(object_id=project_id(322615),
    #                                                                                 object_type="project"),
    #                                                        permission="edit",
    #                                                        subject=SubjectReference(object=ObjectReference(object_type="user", object_id=user_id(322615)))))

    # print(result)r
    # print(datetime.now())
    get_permitted_by_lookup()