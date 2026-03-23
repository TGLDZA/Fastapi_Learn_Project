import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 创建Redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis服务主机地址
    port=REDIS_PORT,  # Redis服务端口号
    db=REDIS_DB,  # Redis数据库编号 0~15
    decode_responses=True  # 将字节流解码成字符串
)