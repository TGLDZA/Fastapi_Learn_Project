# 新闻相关的缓存方法
from typing import Any, List, Dict, Optional

from config.cache_conf import get_json_cache, set_cache

# key要保证唯一性
CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY_PREFIX = "news_list:"
NEWS_DETAIL_KEY_PREFIX = "news:detail:"
RELATED_NEWS_KEY_PREFIX = "news:related:"


# 新闻分类的读取和写入

# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

# 写入新闻分类缓存：缓存的数据，过期时间
# 分类、配置：7200； 列表：600；详情：1800；验证码：120
# 一般数据越稳定，缓存越持久
# 避免key同时过期，引起缓存雪崩
async def set_cached_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 新闻列表的读取和写入
# 写入缓存：新闻列表key：news_list:分类id:页码:该页大小  value: 新闻列表  expire:1800
async def set_cached_news_list(category_id: Optional[int], page:int, page_size: int, news_list: List[Dict[str, Any]], expire: int = 600):
    # 调用封装的 Redis 设置和读取方法，存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return await set_cache(key, news_list, expire)

# 读取缓存--新闻列表
async def get_cached_news_list(category_id: Optional[int], page:int, page_size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)


# 新闻详情缓存的写入和读取

# 写入缓存：新闻详情key：news:detail:新闻id  value: 新闻详情  expire: 1800
async def set_cached_news_detail(news_id: int, news_detail: Dict[str, Any], expire: int = 1800):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await set_cache(key, news_detail, expire)

# 读取新闻详情缓存
async def get_cached_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await get_json_cache(key)


# 相关新闻缓存的写入和读取

# 写入缓存：相关新闻key：news:related:分类id:新闻id  value: 相关新闻列表  expire: 600
async def set_cached_related_news(category_id: int, news_id: int, related_news: List[Dict[str, Any]], expire: int = 600):
    key = f"{RELATED_NEWS_KEY_PREFIX}{category_id}:{news_id}"
    return await set_cache(key, related_news, expire)

# 读取缓存--相关新闻
async def get_cached_related_news(category_id: int, news_id: int):
    key = f"{RELATED_NEWS_KEY_PREFIX}{category_id}:{news_id}"
    return await get_json_cache(key)

