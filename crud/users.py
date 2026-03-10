import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from starlette.exceptions import HTTPException

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
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


# 根据Token查用户 -> 验证Token -> 查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token.token or db_token.expires_at < datetime.now():
        return None

    stmt = select(User).where(User.id == db_token.user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 更新用户信息: update更新 -> 检查是否命中 -> 返回更新后的用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # valuse()里面要满足字段=值，这里是多个字段
    # 可以使用pydantic的model_dump()方法，会将pydantic对象拆解成字典
    # 再用**解包得到的字典就满足values的要求
    stmt = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,  # 未设置的值不提取
        exclude_none=True  # 值为none的不提取
    ))
    result = await db.execute(stmt)
    await db.commit()

    # 检查更新，如果无更新，说明数据库中不存在该用户
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="该用户不存在")

    updated_user = await get_user_by_username(db, username)
    return updated_user


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    # 验证密码
    if not security.verify_password(old_password, user.password):
        return False

    # 新密码加密
    hash_new_pwd = security.get_hash_password(new_password)
    user.password = hash_new_pwd
    # 此处add语句作用：由 SQLAlchemy 接管 User 对象，确保可以commit
    # 规避 session 过期或者不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True