from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.users import get_user_by_token


# 整合 根据 Token 查询用户 返回用户
async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db)
):
    # 由于前端传的请求头字段中 token 格式为 Bearer <token>，所以需要去掉前面的"Bearer "字段才能获得token
    token = authorization.replace("Bearer ", "")
    user = await get_user_by_token(db, token)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌或者令牌已过期")

    return user