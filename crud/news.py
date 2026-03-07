from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.news import Category, List

async def get_news_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession, category_id: int, page: int = 1, page_size: int = 10):
    offset = (page - 1) & page_size
    query = (
        select(List)
        .where(List.category_id == category_id)
        .order_by(List.publish_time)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_news_count(db: AsyncSession, category_id: int) -> int:
    query = (
        select(func.count())
        .select_from(List)
        .where(List.category_id == category_id)
    )
    result = await db.execute(query)
    count = result.scalar()
    return count or 0

