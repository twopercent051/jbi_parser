from pydantic import BaseModel
from sqlalchemy import MetaData, inspect, Column, String, insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, as_declarative

from settings import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class JBIItems(Base):
    """Класс модели БД"""
    __tablename__ = 'jbi_items'

    title = Column(String, nullable=False)
    href = Column(String, nullable=False, primary_key=True)
    parent_1 = Column(String, nullable=False, default='')
    parent_2 = Column(String, nullable=False, default='')
    parent_3 = Column(String, nullable=False, default='')
    parent_4 = Column(String, nullable=False, default='')
    parameters = Column(String, nullable=False)
    image = Column(String, nullable=False)


class SJBIItems(BaseModel):
    """Базовая модель"""

    title: str
    href: str
    parent_1: str
    parent_2: str
    parent_3: str
    parent_4: str
    parameters: str
    image: str


class JBIItemsDAO(JBIItems):
    """Класс взаимодействия с БД"""
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(JBIItems).values(**data)
            await session.execute(stmt)
            await session.commit()
