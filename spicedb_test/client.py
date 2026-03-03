from authzed.api.v1 import InsecureClient


class SpiceDBClient:
    def __init__(self):
        self.client = None

    def init_spicedb_client(self):
        self.client = InsecureClient("localhost:50051", "spicy")


spicedb_client = SpiceDBClient()
