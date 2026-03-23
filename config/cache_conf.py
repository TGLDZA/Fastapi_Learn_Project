import json
from typing import Any

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



# 二次封装Redis 设置 和 读取 （字符串类型， 列表和字典类型）
# 读取的是字符串类型
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e} ")
        return None

# 读取的是列表或字典类型
async def get_json_cache(key: str):
    try:
        result = await redis_client.get(key)
        if result:
            return json.load(result)  # json序列化成列表或字典
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败：{e} ")
        return None

# 设置缓存 setex(key,expire，value)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (list, dict)):
            # 如果是列表或者字典要先转字符串再存
            value = json.dumps(value, ensure_ascii=False)  # 后面设置False表示中文正常保存
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e} ")
        return False