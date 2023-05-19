import asyncio

from pydantic import BaseModel
from sqlalchemy import MetaData, inspect, Column, String, insert, select, Boolean, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, as_declarative
from transliterate import slugify

from settings import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Base = declarative_base()


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
    is_saved = Column(Boolean, nullable=True)
    tranlited_title = Column(String, nullable=True)


class JBIFails(Base):
    """Не сохраненные картинки"""
    __tablename__ = 'jbi_fails'

    title = Column(String, nullable=False)
    image = Column(String, nullable=False, primary_key=True)
    is_saved = Column(Boolean, nullable=False, server_default='false')


class JBIItemsDAO(JBIItems):
    """Класс взаимодействия с БД"""
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(JBIFails).values(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def select_by_href(cls, href: str):
        async with async_session_maker() as session:
            query = select(JBIItems).filter_by(href=href)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def select_failed(cls):
        async with async_session_maker() as session:
            query = select(JBIFails.__table__.columns).filter_by(is_saved=False).limit(1).with_for_update()
            image = await session.execute(query)
            result = image.mappings().one_or_none()
            if result:
                stmt = update(JBIFails).values(is_saved=True).filter_by(image=result['image'])
                await session.execute(stmt)
                await session.commit()
            return result

    @classmethod
    async def update_main(cls, image):
        async with async_session_maker() as session:
            stmt = update(JBIItems).values(is_saved=False).filter_by(image=image)
            await session.execute(stmt)
            await session.commit()


# print(asyncio.run(JBIItemsDAO.select_not_saved()))
#