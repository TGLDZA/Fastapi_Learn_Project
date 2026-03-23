from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_news_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    existing_history = result.scalar_one_or_none()
    # if existing_history:
    #     stmt = (update(History)
    #             .where(History.user_id == user_id, History.news_id == news_id)
    #             .values(view_time=datetime.now()))
    #     new_history = await db.execute(stmt)
    #     await db.commit()
    #     return new_history
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history

    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)

    return history

async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 浏览历史总量
    stmt = select(func.count()).where(History.user_id == user_id)
    result = await db.execute(stmt)
    total = result.scalar_one()

    # 浏览历史列表
    offset = (page - 1) * page_size
    stmt = (select(News, History.id.label("history_id")).join(History, History.news_id == News.id)
     .where(History.user_id == user_id)
     .order_by(History.view_time.desc())
     .offset(offset)
     .limit(page_size))

    result = await db.execute(stmt)
    rows = result.all()

    return total, rows