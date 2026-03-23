from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class HistoryAddRequest(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    news_id: int = Field(alias="newsId")
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )