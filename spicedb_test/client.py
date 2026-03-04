from authzed.api.v1 import InsecureClient, WatchRequest


class SpiceDBClient:
    def __init__(self):
        self.client = None

    def init_spicedb_client(self):
        self.client = InsecureClient("localhost:50051", "spicy")

    def watch_relationships(self, start_token=None):
        request = WatchRequest()

        if start_token:
            request.optional_start_cursor.token = start_token

        stream = self.client.Watch(request)

        for event in stream:
            yield event


spicedb_client = SpiceDBClient()
