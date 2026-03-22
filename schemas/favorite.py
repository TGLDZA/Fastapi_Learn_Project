from pydantic import BaseModel, Field, ConfigDict


# 构造检查收藏状态的pydantic对象
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

# 收藏列表接口的响应模型类
class FavoriteListResponse(BaseModel):
    list: list[xx]
    total: int
    hasmore: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )