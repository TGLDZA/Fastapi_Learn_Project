from pydantic import BaseModel, Field

# 构造检查收藏状态的pydantic对象
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")