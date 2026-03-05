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
        self.token_Key = 'TOKEN'

    def get_client(self):
        return self.client

    def health_check(self):
        return self.client.ping()

    def set_version(self, new_token: str ) :
        self.client.set(self.token_Key, new_token)

    def get_last_version(self) -> str | None:
        return self.client.get(self.token_Key) or None

    def remove(self,key,value):
        self.client.srem(key, value)
        if self.client.scard(key) == 0:
            self.client.delete(key)

    def print_data(self):
        for key in self.client.scan_iter("*"):
            if key != self.token_Key:
                values = redis_client.smembers(key)
                print(f"{key} -> {values}")



redis_wrapper = RedisClient(host="localhost", port=6379)
redis_client = redis_wrapper.get_client()

print(redis_wrapper.health_check())


