from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest
from crud import users
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def user_register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑：验证用户是否存在 -> 创建用户 -> 生成Token -> 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")

    # 此处有一点逻辑问题：如果token创建出错，那么会导致用户注册成功但是token没有创建无法登录
    # 解决办法可以是把整个路由函数当成一个事务，如果任意环节出错就会回滚
    # 或者在crud层不提交数据库，由路由层统一提交
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,  # 注册的时候返回token前端就可以直接登录了
    #         "user_Info": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }

    # model_validate()方法用于从orm对象中提取值
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)

@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 用户登录逻辑：验证用户是否存在 -> 验证密码是否正确 -> 生成Token -> 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    # 具体的业务错误还是要写抛出异常，不然就会进入token创建出错，就变成了数据库完整性约束错误
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或者密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)

# 查Token 查用户 -> 封装crud -> 功能整合成一个工具函数 -> 路由函数调用
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息 -> 验证Token -> 更新用户信息（用户输入数据 put提交 -> 请求体参数 -> 定义模型类，pydantic校验） -> 响应结果
# 参数： 用户输入 + 验证Token的 + db（调用更新的方法）
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest,
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)
                           ):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更改信息成功", data=UserInfoResponse.model_validate(user))