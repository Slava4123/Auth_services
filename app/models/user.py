from sqlalchemy import Column, Integer, String, Boolean
from app.database.db_connection import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String, default=True)
    role = Column(String)
    is_admin = Column(Boolean)


