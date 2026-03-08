from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models.news import Category, News

async def get_news_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

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

async def get_related_news(db: AsyncSession, category_id: int, news_id: int, limit: int = 3):
    # 查询指定id的相关新闻
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .where(News.id != news_id)
        .order_by(func.random())
        .limit(limit)
    )
    results = await db.execute(stmt)
    return results.scalars().all()

async def increase_news_views(db: AsyncSession, news_id: int):
    # 增加浏览量
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    await db.execute(stmt)
    await db.commit()  # 增加确定性，执行完立即提交