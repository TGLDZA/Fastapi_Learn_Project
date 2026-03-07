from fastapi import APIRouter, Depends

import crud.news
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
async def get_news_list(categoryId: int, page: int = 1, pageSize: int = 10, db: AsyncSession = Depends(get_db)):
    news_list = await crud.news.get_news_list(db, categoryId, page, pageSize)
    total = await crud.news.get_news_count(db, categoryId)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    }