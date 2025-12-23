from app.database import Base
from sqlalchemy import Column, Integer, String


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)