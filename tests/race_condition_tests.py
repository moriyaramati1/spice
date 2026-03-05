import random
import string
import unittest
import threading
import time

from authzed.api.v1 import RelationshipUpdate

from redis_client import redis_client, redis_wrapper
from redis_update import activate_watch_listener
from spicedb_test.client import spicedb_client


class TestWatchUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redis_client = redis_client
        cls.redis_client.flushdb()
        cls.spicedb_client = spicedb_client


    def update_relationships(self, relationships,operation):
        self.spicedb_client.bulk_write_relationships(relationships,operation)

    def threading(self,relationships_first_group,relationships_second_group,first_operation,second_operation):
        listener_thread = threading.Thread(target=activate_watch_listener)
        listener_thread.daemon = True
        listener_thread.start()
        time.sleep(20)

        t1 = threading.Thread(target=self.update_relationships, args=(relationships_first_group,first_operation,))
        t2 = threading.Thread(target=self.update_relationships, args=(relationships_second_group,second_operation))

        # Act
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def random_string(self, length=8):
        letters_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_digits) for _ in range(length))

    def randomize_relations(self,first_user, second_user, first_project,second_project,multiple_relationships_number: None | int = None):
        # Arrange
        if multiple_relationships_number is None:
            relationships_first_group = [
                {
                    "resource_type": "project",
                    "resource_id": first_project,
                    "relation": "owner",
                    "subject_type": "user",
                    "subject_id": first_user,
                }]

            relationships_second_group = [
                {
                    "resource_type": "project",
                    "resource_id": second_project,
                    "relation": "owner",
                    "subject_type": "user",
                    "subject_id": second_user,
                }]
        else:
            relationships_first_group = [
                {
                    "resource_type": "project",
                    "resource_id": f"{first_project}{i}",
                    "relation": "owner",
                    "subject_type": "user",
                    "subject_id": first_user,
                } for i in range(multiple_relationships_number)]

            relationships_second_group = [
                {
                    "resource_type": "project",
                    "resource_id": f"{second_project}{i}",
                    "relation": "owner",
                    "subject_type": "user",
                    "subject_id": second_user,
                } for i in range(multiple_relationships_number)]

            shuffled_relationships_first_group = relationships_first_group[0:multiple_relationships_number//2] + relationships_second_group[0:multiple_relationships_number//2]
            shuffled_relationships_second_group = relationships_first_group[multiple_relationships_number//2:] + relationships_second_group[multiple_relationships_number//2 : ]
            relationships_first_group = shuffled_relationships_first_group
            relationships_second_group = shuffled_relationships_second_group


        return relationships_first_group, relationships_second_group

    def test_parallel_update_relations(self):
        first_project = self.random_string()
        second_project = self.random_string()
        first_user = self.random_string()
        second_user = self.random_string()

        relationships_first_group, relationships_second_group = self.randomize_relations(first_user,second_user, first_project ,second_project)

        self.threading(relationships_first_group,relationships_second_group,
                       RelationshipUpdate.OPERATION_TOUCH,
                       RelationshipUpdate.OPERATION_TOUCH)

        # Assert
        assert self.redis_client.smembers(f"project:{first_user}:owner") == {f"{first_project}"}
        assert self.redis_client.smembers(f"project:{second_user}:owner") == {f"{second_project}"}
        assert redis_wrapper.get_last_version() is not None


    def test_parallel_opposite_actions(self):
        first_project = self.random_string()
        second_project = self.random_string()
        first_user = self.random_string()

        self.redis_client.sadd(f"project:{first_user}:owner", second_project)
        relationships_first_group, relationships_second_group = self.randomize_relations(first_user,first_user, first_project ,second_project)
        self.update_relationships(relationships_second_group,RelationshipUpdate.OPERATION_TOUCH)

        self.threading(relationships_first_group, relationships_second_group,
                       RelationshipUpdate.OPERATION_TOUCH,
                       RelationshipUpdate.OPERATION_DELETE)


        assert self.redis_client.smembers(f"project:{first_user}:owner") == {f"{first_project}"}
        assert redis_wrapper.get_last_version() is not None


    def test_load_testing_with_multiple_threads(self):
        first_project = self.random_string()
        second_project = self.random_string()
        first_user = self.random_string()
        second_user = self.random_string()
        TOTAL = 1000

        relationships_first_group, relationships_second_group = self.randomize_relations(first_user,second_user,
                                                                                         first_project ,second_project, TOTAL)

        self.threading(relationships_first_group,relationships_second_group,
                               RelationshipUpdate.OPERATION_TOUCH,
                               RelationshipUpdate.OPERATION_TOUCH)


        time.sleep(10)
        # Assert
        assert len(self.redis_client.smembers(f"project:{first_user}:owner")) == TOTAL
        assert len(self.redis_client.smembers(f"project:{second_user}:owner")) == TOTAL
        assert redis_wrapper.get_last_version() is not None



