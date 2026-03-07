from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="更新时间"
    )

class Category(Base):

    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类id")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    # 打印对象， 便于观察
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"

class List(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻id")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[str] = mapped_column(String(500),nullable=False, comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[str] = mapped_column(String(255), comment="新闻图片")
    author: Mapped[str] = mapped_column(String(50),nullable=False, comment="新闻作者")
    category_id: Mapped[int] = mapped_column(Integer,ForeignKey("news_category.id"), nullable=False, comment="新闻所属分类")
    views: Mapped[int] = mapped_column(Integer, default=0,nullable=False, comment="观看数量")
    publish_time: Mapped[datetime] = mapped_column(DateTime,default=datetime.now, comment="发布时间")

    def __repr__(self):
        return (f"<List(id={self.id}, title={self.title}, description={self.description},"
                f"content={self.content}, image={self.image}, author={self.author},"
                f"category_id={self.category_id}, views={self.views}, publish_time={self.publish_time})>")