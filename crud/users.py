import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import User, UserToken
from schemas.users import UserRequest
from utils import security
from utils.security import verify_password


async def get_user_by_username(db: AsyncSession, username: str):
    # 根据用户名查询数据库
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRequest):
    # 先对明文密码进行加密
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库中读回最新的user
    return user


# 生成Token
async def create_token(db: AsyncSession, user_id: int):
    # 生成Token + 设置过期时间 -> 查询数据库当前用户是否有 token -> 有则更新，无则添加
    token = str(uuid.uuid4())
    # timedelta(days=7, hours=6, minutes=5, seconds=4)  # 设置时间长度
    expires_at = datetime.now() + timedelta(days=7)

    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()

    if user_token:
       user_token.token = token
       user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    # 该用户不存在
    if not user:
        return None
    # 密码不对
    if not verify_password(password, user.password):
        return None

    return user