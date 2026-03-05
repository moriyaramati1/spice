from authzed.api.v1 import RelationshipUpdate
from redis_client import redis_wrapper, redis_client
from spicedb_test.client import spicedb_client


for event in spicedb_client.watch_relationships(redis_wrapper.get_last_version()):
    redis_wrapper.set_version(event.changes_through.token)

    for update in event.updates:
        relation = update.relationship
        key = f"{relation.resource.object_type}:{relation.subject.object.object_id}:{relation.relation}"
        value = relation.resource.object_id
        if update.operation == RelationshipUpdate.OPERATION_DELETE:
            redis_wrapper.remove(key,value)
        else:
            redis_client.sadd(key, value)

