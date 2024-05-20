import aioredis 


REDIS_URL = 'redis://127.0.0.1:6379'
REDIS_DB = 0
REDIS_PASSWORD = None



def get_redis_pool():

    
    POOL =  aioredis.from_url(
        REDIS_URL,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        encoding="utf-8", 
        decode_responses=True
        )
                

    return POOL