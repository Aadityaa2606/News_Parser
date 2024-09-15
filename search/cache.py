import redis
from django.conf import settings

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


def cache_set(key, value, timeout=3600):
    redis_client.setex(key, timeout, value)


def cache_get(key):
    return redis_client.get(key)


def cache_delete(key):
    redis_client.delete(key)

def cache_ttl(key):
    return redis_client.ttl(key)