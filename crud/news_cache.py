from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_news_list, set_cached_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


# 旁路策略：先从缓存中读数据，若没有则从数据库中查询读取，写入缓存后再返回数据

async def get_news_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中读取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    # 如果没有则继续查数据库
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # ORM对象

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)  # 将ORM对象转json
        await set_cached_categories(categories)

    # 返回数据
    return categories

async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):

    # 先尝试从缓存中获取新闻列表
    page = (skip // limit) + 1
    cached_news_list = await get_cached_news_list(category_id, page, limit)  # 得到的是缓存数据json
    if cached_news_list:
        # 这里需要返回ORM对象
        return [News(**item) for item in cached_news_list]

    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把ORM数据转换成字典才能写入缓存
        # 这里也可以用jsonable.encoder()
        # 此处使用另一种方法： ORM转pydantic再转字典
        # by_alias=False 不使用别名，保持Python风格，因为Redis数据是给后端用的
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cached_news_list(category_id, page, limit, news_data)

    # 响应数据
    return news_list

async def get_news_count(db: AsyncSession, category_id: int) -> int:
    # 查询的是指定分类下的数量
    stmt = (
        select(func.count(News.id)).
        where(News.category_id == category_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，否则报错

async def get_news_detail(db: AsyncSession, news_id: int):
    # 查询指定id的新闻详情
    return await db.get(News, news_id)

async def get_related_news(db: AsyncSession, category_id: int, news_id: int, limit: int = 5):
    # 查询指定id的相关新闻
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .where(News.id != news_id)
        .order_by(  # 浏览量最高，发布时间最新的前五名推荐
            News.views.desc(),
            News.publish_time.desc()
        ).limit(limit)
    )
    results = await db.execute(stmt)
    return results.scalars().all()

async def increase_news_views(db: AsyncSession, news_id: int):
    # 增加浏览量
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()  # 增加确定性，执行完立即提交

    # 检查数据库是否真的命中了数据 -> 命中了返回True
    return result.rowcount > 0