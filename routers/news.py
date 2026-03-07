from fastapi import APIRouter

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
async def get_news_categories(skip: int = 0, limit: int = 100):
    return {
        "code": 200,
        "message": "success",
        "data": "新闻分类列表"
    }