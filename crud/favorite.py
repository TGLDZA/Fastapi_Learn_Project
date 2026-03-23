from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# 检查收藏状态：当前用户 是否收藏了 这一条新闻
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):

    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    # 是否有收藏记录，返回布尔值
    return result.scalar_one_or_none() is not None

async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# 获取收藏列表：获取的是某个用户的收藏列表和分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 需要获取的是新闻总量和新闻列表

    # 获取新闻列表的新闻总量，用聚合查询
    stmt = select(func.count()).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    total = result.scalar_one()

    # 联表查询新闻列表，收藏时间排序 + 分页
    # 用法：select(主体模型类， 字段别名).join(联表模型类，联表条件).where().order_by()
    # 字段别名用法：Favorite.created_time.label("favorite_time")
    # 本处得到的是一个元组列表，格式为:
    # [
    #     (新闻对象, 收藏时间, 收藏id)
    # ]
    offset = (page - 1) * page_size
    stmt = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id")).join(Favorite, Favorite.news_id == News.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc()).
            offset(offset)
            .limit(page_size))
    result = await db.execute(stmt)
    rows = result.all()

    return total, rows

async def remove_all_favorite(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回删除的记录数
    return result.rowcount() or 0