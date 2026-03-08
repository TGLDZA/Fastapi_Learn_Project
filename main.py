from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db_conf import async_engine
from routers import news, users
from utils.exception_handlers import register_error_handlers

app = FastAPI()

# 注册异常处理器
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，生产环境可以写*允许全部，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"]  # 允许的请求头
)

@app.on_event("shutdown")
async def shutdown_db():
    """应用关闭时清理数据库连接"""
    await async_engine.dispose()  # ✅ 释放所有连接


@app.get("/")
async def root():
    return {"message": "Hello World"}
# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
