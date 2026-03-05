from authzed.api.v1 import InsecureClient, WatchRequest, WriteRelationshipsRequest, SubjectReference, ObjectReference, \
    Relationship, RelationshipUpdate, LookupSubjectsRequest, LookupResourcesRequest, Consistency


class SpiceDBClient:
    def __init__(self):
        self.client = None

    def init_spicedb_client(self):
        self.client = InsecureClient("localhost:50051", "spicy")

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

    def bulk_write_relationships(self, relationships:list,
                                 operation: RelationshipUpdate = RelationshipUpdate.OPERATION_TOUCH):
        updates = []

        for r in relationships:
            updates.append(
                RelationshipUpdate(
                    operation=operation,
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

        print('start_token',start_token)
        if start_token:
            request.optional_start_cursor.token = start_token

        stream = self.client.Watch(request)

        for event in stream:
            yield event

spicedb_client = SpiceDBClient()
