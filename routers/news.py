from fastapi import APIRouter, Depends, Query, HTTPException
from crud import news
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# 创建 APIRouter 实例
# prefix 路由前缀
# tags 分组 标签
router = APIRouter(prefix="/api/news", tags=["news"])

# 接口实现流程
# 1. 模块化路由 -> API接口规范文档
# 2. 定义模型类 -> 数据库表（数据库设计文档）
# 3. 在 crud 目录封装操作数据库的防范
# 4. 在路由处理函数调用 crud 封装好的方法，响应结果

@router.get("/categories")
async def get_news_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # 先获取数据库新闻分类 -> 先定义模型类 -> 封装查询数据的方法
    categories = await news.get_news_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, le=100, alias="pageSize"),
        db: AsyncSession = Depends(get_db)
):

    # 处理分页规则 -> 查询新闻列表 -> 计算总量 -> 计算是否还有更多
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    hasmore = (offset + len(news_list)) < total

    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasmore": hasmore
        }
    }

@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_db)
):

    # 获取新闻详情 + 浏览量 + 1 + 获取相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="获取内容不存在")
    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="获取内容不存在")
    related_news = await news.get_related_news(db, news_detail.category_id, news_id, limit=3)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }