import redis
from redis.connection import ConnectionPool

class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            max_connections=50
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def get_client(self):
        return self.client

    def health_check(self):
        return self.client.ping()


# Usage
redis_wrapper = RedisClient(host="localhost", port=6379)
redis_client = redis_wrapper.get_client()

print(redis_wrapper.health_check())


