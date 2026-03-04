from authzed.api.v1 import (
    LookupResourcesRequest,
    LookupSubjectsRequest,
    ObjectReference,
    SubjectReference,
    InsecureClient,
    Consistency, WriteRelationshipsRequest, RelationshipUpdate, Relationship, WatchRequest, WriteSchemaRequest,
)

from authzed.api.v1.watch_service_pb2 import WatchRequest

from redis_client import redis_client


class SpiceDBClient:
    def __init__(self, endpoint: str, token: str = None, insecure: bool = True):
        self.metadata = [("authorization", "Bearer spicy")]
        self.client = InsecureClient(endpoint,token)


    def build_consistency(self, mode="minimize_latency", zed_token=None):
        if mode == "fully_consistent":
            return Consistency(fully_consistent=True)

        elif mode == "at_least_as_fresh" and zed_token:
            return Consistency(
                at_least_as_fresh=Consistency.AtLeastAsFresh(
                    token=zed_token
                )
            )

        elif mode == "at_exact_snapshot" and zed_token:
            return Consistency(
                at_exact_snapshot=Consistency.AtExactSnapshot(
                    token=zed_token
                )
            )

        return Consistency(minimize_latency=True)

    def lookup_resources(
        self,
        resource_type,
        permission,
        subject_type,
        subject_id,
        consistency_mode="minimize_latency",
        zed_token=None,
    ):
        request = LookupResourcesRequest(
            resource_object_type=resource_type,
            permission=permission,
            subject=SubjectReference(
                object=ObjectReference(
                    object_type=subject_type,
                    object_id=subject_id,
                )
            ),
            consistency=self.build_consistency(consistency_mode, zed_token),
        )

        for response in self.client.LookupResources(request):
            yield response.resource_object_id


    def lookup_subjects(
        self,
        resource_type,
        resource_id,
        permission,
        subject_type,
        consistency_mode="minimize_latency",
        zed_token=None,
    ):
        request = LookupSubjectsRequest(
            resource=ObjectReference(
                object_type=resource_type,
                object_id=resource_id,
            ),
            permission=permission,
            subject_object_type=subject_type,
            consistency=self.build_consistency(consistency_mode, zed_token),
        )

        for response in self.client.LookupSubjects(request):
            yield response.subject_object_id

    def write_relationship(
            self,
            resource_type,
            resource_id,
            relation,
            subject_type,
            subject_id,
    ):
        request = WriteRelationshipsRequest(
            updates=[
                RelationshipUpdate(
                    operation=RelationshipUpdate.OPERATION_TOUCH,
                    relationship=Relationship(
                        resource=ObjectReference(
                            object_type=resource_type,
                            object_id=resource_id,
                        ),
                        relation=relation,
                        subject=SubjectReference(
                            object=ObjectReference(
                                object_type=subject_type,
                                object_id=subject_id,
                            )
                        ),
                    ),
                )
            ]
        )



        response = self.client.WriteRelationships(request)
        return response.written_at.token

    def bulk_write_relationships(self, relationships):
        updates = []

        for r in relationships:
            updates.append(
                RelationshipUpdate(
                    operation=RelationshipUpdate.OPERATION_TOUCH,
                    relationship=Relationship(
                        resource=ObjectReference(
                            object_type=r["resource_type"],
                            object_id=r["resource_id"],
                        ),
                        relation=r["relation"],
                        subject=SubjectReference(
                            object=ObjectReference(
                                object_type=r["subject_type"],
                                object_id=r["subject_id"],
                            )
                        ),
                    ),
                )
            )

        request = WriteRelationshipsRequest(updates=updates)
        response = self.client.WriteRelationships(request)
        return response.written_at.token

    def watch_relationships(self, start_token=None):
        request = WatchRequest()

        if start_token:
            request.optional_start_cursor.token = start_token

        stream = self.client.Watch(request)

        for event in stream:
            yield event

import grpc
channel = grpc.insecure_channel("localhost:50051")
grpc.channel_ready_future(channel).result(timeout=5)  # should succeed
print("Channel ready")

spice_handler = SpiceDBClient("localhost:50051","spicy")


for key in redis_client.scan_iter("*"):
    values = redis_client.smembers(key)
    print(f"{key} -> {values}")


for event in spice_handler.watch_relationships():
    print("New change detected")
    for update in event.updates:
        relation = update.relationship
        redis_client.sadd(f"{relation.resource.object_type}:{relation.subject.object.object_id}:{relation.relation}", relation.resource.object_id)



