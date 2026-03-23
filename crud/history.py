from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History


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