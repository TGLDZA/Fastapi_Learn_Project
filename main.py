from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，生产环境可以写*允许全部，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"]  # 允许的请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
# 挂载路由/注册路由
app.include_router(news.router)
